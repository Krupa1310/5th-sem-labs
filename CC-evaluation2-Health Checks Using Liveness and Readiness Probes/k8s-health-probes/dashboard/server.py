"""
Monitoring dashboard backend  (runs INSIDE the cluster)

Everything shown on the dashboard is fetched live:
  * Pods, restart counts, READY state, Service endpoints, events and the
    Deployment come from the Kubernetes API (using the pod's ServiceAccount token).
  * Per-pod application state comes from each pod's own /info endpoint, which also
    reports the last probe request the *kubelet* sent (so we can show real
    liveness/readiness probe results).
No pod status is hard-coded or simulated here.

Buttons -> POST /api/action/...
  liveness-fail   POST /control/liveness  on ONE selected pod
  readiness-fail  POST /control/readiness on ONE selected pod
  slow-startup    PATCH the Deployment: STARTUP_DELAY_SECONDS=30  (real rolling update)
  restore         POST /control/reset on the pods + STARTUP_DELAY_SECONDS back to 0
"""
import json
import os
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory

SA_DIR = "/var/run/secrets/kubernetes.io/serviceaccount"
API = "https://{}:{}".format(os.getenv("KUBERNETES_SERVICE_HOST", "kubernetes.default.svc"),
                             os.getenv("KUBERNETES_SERVICE_PORT", "443"))
DEPLOYMENT = os.getenv("TARGET_DEPLOYMENT", "health-demo")
SERVICE = os.getenv("TARGET_SERVICE", "health-demo-svc")
LABEL = os.getenv("TARGET_LABEL", "app=health-demo")
APP_PORT = int(os.getenv("APP_PORT", "5000"))
SLOW_DELAY = 30  # seconds - value required by the lab brief


def _read(name, default=""):
    try:
        with open(os.path.join(SA_DIR, name)) as f:
            return f.read().strip()
    except OSError:
        return default


NAMESPACE = os.getenv("NAMESPACE") or _read("namespace", "default")

app = Flask(__name__, static_folder="static", static_url_path="/static")
_ctx = None


class K8sError(Exception):
    pass


def _ssl_ctx():
    global _ctx
    if _ctx is None:
        _ctx = ssl.create_default_context(cafile=os.path.join(SA_DIR, "ca.crt"))
    return _ctx


def k8s(method, path, body=None, content_type="application/json"):
    """Call the Kubernetes API with the pod's ServiceAccount token."""
    token = _read("token")
    if not token:
        raise K8sError("No ServiceAccount token found - is the dashboard running inside the cluster?")
    req = urllib.request.Request(API + path, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": content_type, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5, context=_ssl_ctx()) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise K8sError(f"Kubernetes API {e.code} on {method} {path}: {detail}")
    except (urllib.error.URLError, OSError) as e:
        raise K8sError(f"Cannot reach Kubernetes API: {e}")


def pod_call(ip, path, method="GET", body=None, timeout=1.5):
    """Talk to one application pod directly via its Pod IP."""
    req = urllib.request.Request(f"http://{ip}:{APP_PORT}{path}", method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def parse_ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def age_seconds(s):
    t = parse_ts(s) if s else None
    return None if t is None else max(0, int((datetime.now(timezone.utc) - t).total_seconds()))


# ------------------------------------------------------------ pod handling
def kubectl_style_status(p):
    """Reproduce the STATUS column of `kubectl get pods`."""
    if p["metadata"].get("deletionTimestamp"):
        return "Terminating"
    for cs in p["status"].get("containerStatuses", []):
        w = cs["state"].get("waiting")
        if w and w.get("reason"):
            return w["reason"]
        t = cs["state"].get("terminated")
        if t and t.get("reason"):
            return t["reason"]
    return p["status"].get("phase", "Unknown")


def summarize_pod(p):
    cs = p["status"].get("containerStatuses", [])
    conds = {c["type"]: c["status"] for c in p["status"].get("conditions", [])}
    last_term = None
    for c in cs:
        t = c.get("lastState", {}).get("terminated")
        if t:
            last_term = f"{t.get('reason', 'Terminated')} (exit {t.get('exitCode')}) {age_seconds(t.get('finishedAt'))}s ago"
    return {
        "name": p["metadata"]["name"],
        "ip": p["status"].get("podIP"),
        "node": p["spec"].get("nodeName"),
        "phase": p["status"].get("phase"),
        "status": kubectl_style_status(p),
        "ready_str": f"{sum(1 for c in cs if c.get('ready'))}/{len(p['spec']['containers'])}",
        "ready": conds.get("Ready") == "True",
        "restarts": sum(c.get("restartCount", 0) for c in cs),
        "last_termination": last_term,
        "age_seconds": age_seconds(p["metadata"].get("creationTimestamp")),
        "terminating": bool(p["metadata"].get("deletionTimestamp")),
    }


def fetch_info(pod):
    """Ask the pod's own /info endpoint. Returns None if it can't answer."""
    if not pod["ip"] or pod["phase"] != "Running" or pod["terminating"]:
        return None
    try:
        return pod_call(pod["ip"], "/info")
    except Exception:
        return None


def probe_view(info, kind, k8s_ready):
    """Turn the kubelet's last probe (as seen by the app) into a display state."""
    if info is None:
        return {"state": "Unreachable", "detail": "app not answering"}
    lp = (info.get("last_kubelet_probe") or {}).get(kind)
    counts = (info.get("kubelet_probe_counts") or {}).get(kind, {})
    if lp is None:
        return {"state": "Not probed yet", "detail": "waiting for first kubelet probe"}
    ok = lp["status"] < 400
    return {"state": "Passing" if ok else "Failing",
            "detail": f"last kubelet probe: HTTP {lp['status']}, {lp['age_seconds']}s ago "
                      f"({counts.get('ok', 0)} ok / {counts.get('fail', 0)} failed)"}


def get_pods():
    data = k8s("GET", f"/api/v1/namespaces/{NAMESPACE}/pods?labelSelector={LABEL}")
    pods = [summarize_pod(p) for p in data["items"]]
    with ThreadPoolExecutor(max_workers=8) as ex:
        infos = list(ex.map(fetch_info, pods))
    for pod, info in zip(pods, infos):
        pod["app"] = info
        pod["liveness"] = probe_view(info, "liveness", pod["ready"])
        pod["readiness"] = probe_view(info, "readiness", pod["ready"])
        # "Healthy" = Kubernetes says Ready AND the app's liveness endpoint answers 200
        pod["healthy"] = bool(pod["ready"] and info and info.get("healthz_status") == 200 and not pod["terminating"])
    pods.sort(key=lambda p: (p["terminating"], p["name"]))
    return pods


def get_endpoints():
    try:
        ep = k8s("GET", f"/api/v1/namespaces/{NAMESPACE}/endpoints/{SERVICE}")
    except K8sError as e:
        if "404" in str(e):
            return {"ready": [], "not_ready": [], "service_found": False}
        raise
    def addr(a):
        return {"ip": a["ip"], "pod": (a.get("targetRef") or {}).get("name")}
    ready, not_ready = [], []
    for s in ep.get("subsets") or []:
        ready += [addr(a) for a in s.get("addresses") or []]
        not_ready += [addr(a) for a in s.get("notReadyAddresses") or []]
    return {"ready": ready, "not_ready": not_ready, "service_found": True}


def get_deployment():
    d = k8s("GET", f"/apis/apps/v1/namespaces/{NAMESPACE}/deployments/{DEPLOYMENT}")
    c = d["spec"]["template"]["spec"]["containers"][0]
    delay = 0
    for e in c.get("env", []):
        if e["name"] == "STARTUP_DELAY_SECONDS":
            try:
                delay = int(e.get("value", "0"))
            except ValueError:
                delay = 0
    st = d["status"]
    return {"name": DEPLOYMENT, "desired": d["spec"]["replicas"], "ready": st.get("readyReplicas", 0),
            "updated": st.get("updatedReplicas", 0), "available": st.get("availableReplicas", 0),
            "total": st.get("replicas", 0), "startup_delay": delay,
            "container": c["name"], "probes": {"liveness": c.get("livenessProbe"), "readiness": c.get("readinessProbe")}}


def get_events(pod_names):
    data = k8s("GET", f"/api/v1/namespaces/{NAMESPACE}/events?fieldSelector=involvedObject.kind=Pod")
    out = []
    for e in data["items"]:
        name = e["involvedObject"].get("name", "")
        if not name.startswith(DEPLOYMENT + "-"):
            continue
        ts = e.get("lastTimestamp") or e.get("eventTime") or e["metadata"].get("creationTimestamp")
        out.append({"ts": ts, "age_seconds": age_seconds(ts), "type": e.get("type"), "reason": e.get("reason"),
                    "pod": name, "message": e.get("message", ""), "count": e.get("count", 1)})
    out.sort(key=lambda x: x["ts"] or "", reverse=True)
    return out[:25]


def derive_scenario(pods, dep):
    """What failure is currently active? Derived from live pod + deployment state."""
    live = [p for p in pods if p["app"] and p["app"]["liveness_failure_injected"]]
    rdy = [p for p in pods if p["app"] and p["app"]["readiness_failure_injected"]]
    slow = [p for p in pods if p["app"] and p["app"]["startup_remaining_seconds"] > 0]
    details, names = [], []
    if live:
        names.append("Liveness failure")
        details.append("/healthz returns 500 on: " + ", ".join(p["name"] for p in live))
    if rdy:
        names.append("Readiness failure")
        details.append("/ready returns 503 on: " + ", ".join(p["name"] for p in rdy))
    if slow or dep["startup_delay"] > 0:
        names.append("Slow startup")
        details.append(f"Deployment start-up delay = {dep['startup_delay']}s"
                       + (f"; still initialising: {', '.join(p['name'] for p in slow)}" if slow else ""))
    return {"name": " + ".join(names) if names else "None - normal operation", "active": bool(names), "details": details}


@app.get("/api/status")
def status():
    try:
        pods = get_pods()
        dep = get_deployment()
        eps = get_endpoints()
        events = get_events([p["name"] for p in pods])
    except K8sError as e:
        return jsonify(error=str(e)), 502
    live_pods = [p for p in pods if not p["terminating"]]
    healthy = [p for p in live_pods if p["healthy"]]
    ready = [p for p in live_pods if p["ready"]]
    if not live_pods or not healthy:
        overall = "DOWN"
    elif len(healthy) == len(live_pods) == dep["desired"]:
        overall = "HEALTHY"
    else:
        overall = "DEGRADED"
    return jsonify(
        time=datetime.now(timezone.utc).isoformat(), namespace=NAMESPACE,
        totals={"pods": len(live_pods), "healthy": len(healthy), "unhealthy": len(live_pods) - len(healthy),
                "ready": len(ready), "not_ready": len(live_pods) - len(ready),
                "restarts": sum(p["restarts"] for p in live_pods), "desired": dep["desired"]},
        overall=overall, scenario=derive_scenario(live_pods, dep),
        pods=pods, endpoints=eps, deployment=dep, events=events)


# ------------------------------------------------------------------ actions
def find_pod(name):
    """Resolve a pod NAME to its IP using the Kubernetes API (we never trust an IP from the browser)."""
    for p in get_pods_basic():
        if p["name"] == name:
            return p
    raise K8sError(f"Pod '{name}' not found")


def get_pods_basic():
    data = k8s("GET", f"/api/v1/namespaces/{NAMESPACE}/pods?labelSelector={LABEL}")
    return [summarize_pod(p) for p in data["items"]]


def set_startup_delay(seconds):
    patch = {"spec": {"template": {"spec": {"containers": [
        {"name": get_deployment()["container"], "env": [{"name": "STARTUP_DELAY_SECONDS", "value": str(seconds)}]}]}}}}
    k8s("PATCH", f"/apis/apps/v1/namespaces/{NAMESPACE}/deployments/{DEPLOYMENT}", patch,
        content_type="application/strategic-merge-patch+json")


@app.post("/api/action/<name>")
def action(name):
    body = request.get_json(silent=True) or {}
    pod_name = body.get("pod")
    try:
        if name in ("liveness-fail", "readiness-fail"):
            if not pod_name:
                return jsonify(error="Select a pod first."), 400
            pod = find_pod(pod_name)
            if pod["terminating"] or not pod["ip"]:
                return jsonify(error=f"{pod_name} is not available."), 409
            kind = "liveness" if name == "liveness-fail" else "readiness"
            pod_call(pod["ip"], f"/control/{kind}", "POST", {"fail": True}, timeout=3)
            msg = (f"/healthz on {pod_name} now returns 500. After 3 failed probes (~15 s) Kubernetes will restart the container."
                   if kind == "liveness" else
                   f"/ready on {pod_name} now returns 503. After 3 consecutive failed probes (~15 s; failureThreshold defaults to 3) it becomes NotReady and leaves the Service endpoints.")
            return jsonify(ok=True, message=msg)

        if name == "slow-startup":
            set_startup_delay(SLOW_DELAY)
            return jsonify(ok=True, message=f"Deployment patched: STARTUP_DELAY_SECONDS={SLOW_DELAY}. "
                                            "Kubernetes is rolling out new pods that stay 0/1 Ready for ~30 s.")

        if name == "restore":
            msgs = []
            if get_deployment()["startup_delay"] != 0:
                set_startup_delay(0)
                msgs.append("start-up delay set back to 0 (rolling update)")
            targets = [p for p in get_pods_basic() if p["ip"] and not p["terminating"] and p["phase"] == "Running"
                       and (not pod_name or p["name"] == pod_name)]
            def reset(p):
                try:
                    pod_call(p["ip"], "/control/reset", "POST", {}, timeout=3)
                    return True
                except Exception:
                    return False
            with ThreadPoolExecutor(max_workers=8) as ex:
                done = sum(ex.map(reset, targets))
            msgs.append(f"cleared injected failures on {done}/{len(targets)} pod(s)")
            return jsonify(ok=True, message="Restored: " + "; ".join(msgs) + ".")

        return jsonify(error=f"Unknown action '{name}'"), 404
    except K8sError as e:
        return jsonify(error=str(e)), 502
    except Exception as e:  # pod unreachable etc.
        return jsonify(error=f"Action failed: {e}"), 502


@app.post("/api/traffic-test")
def traffic_test():
    """Send N requests through the real Service and count which pods answered."""
    n = min(int((request.get_json(silent=True) or {}).get("count", 30)), 100)
    url = f"http://{SERVICE}.{NAMESPACE}.svc.cluster.local/whoami"
    def one(_):
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                return json.load(r)["pod"]
        except Exception:
            return None
    with ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(one, range(n)))
    counts = {}
    for r in results:
        if r:
            counts[r] = counts.get(r, 0) + 1
    return jsonify(sent=n, failed=sum(1 for r in results if r is None), by_pod=counts)


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    print(f"dashboard: namespace={NAMESPACE} deployment={DEPLOYMENT} service={SERVICE}", flush=True)
    app.run(host="0.0.0.0", port=8080, threaded=True)
