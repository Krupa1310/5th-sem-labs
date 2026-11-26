"""
Monitoring dashboard backend  (runs INSIDE the cluster)

Everything shown on the dashboard is fetched live:
  * Pods, restart counts, READY state, Service endpoints, events and the
    Deployment come from the Kubernetes API (using the pod's ServiceAccount token).
  * Per-pod application state comes from each pod's own /info endpoint, which also
    reports the last probe request the *kubelet* sent (so we can show real
    liveness/readiness probe results).
No pod status is hard-coded or simulated here.

Automatic demonstration mode (DEMO_MODE=on)
  A background thread periodically injects ONE short failure (alternating liveness / readiness) into
  ONE pod - but only while every pod is healthy and no other failure is active. Kubernetes' probes
  detect it and recover on their own; the dashboard only records what happened. Every injected
  failure has a built-in expiry inside the app, so it can never become permanent.

Buttons -> POST /api/action/...
  liveness-fail   POST /control/liveness  on ONE selected pod
  readiness-fail  POST /control/readiness on ONE selected pod
  slow-startup    PATCH the Deployment: STARTUP_DELAY_SECONDS=30  (real rolling update)
  restore         POST /control/reset on the pods + STARTUP_DELAY_SECONDS back to 0
"""
import json
import os
import random
import ssl
import threading
import time
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
        pod["startup"] = probe_view(info, "startup", pod["ready"])
        pod["database"] = (info or {}).get("database")
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
            "container": c["name"], "image": c.get("image"),
            "probes": {"startup": c.get("startupProbe"), "liveness": c.get("livenessProbe"),
                       "readiness": c.get("readinessProbe")}}


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



# ------------------------------------------------------- automatic demo mode
def _env_int(name, default, lo, hi):
    try:
        return max(lo, min(int(os.getenv(name, default)), hi))
    except ValueError:
        return default


class DemoMode:
    """Periodically injects one controlled, temporary failure and tracks detection + recovery.

    Safety rules (all enforced in _unsafe_reason / _progress):
      * only ONE failure at a time, never while another failure or a rollout is in progress
      * only when every desired pod is Running, Ready and healthy (so the Service keeps >= 2 pods)
      * the app auto-clears every injected failure after `duration_seconds` even if we vanish
      * anything not recovered after a timeout is force-cleared, so failures are never continuous
      * it never touches the database, so no student data can be lost
    """
    MIN_INTERVAL = 45
    LIVENESS_EXPIRY = 75          # s - well above the ~15 s the kubelet needs to restart the container

    def __init__(self):
        self.lock = threading.RLock()
        self.enabled = os.getenv("DEMO_MODE", "off").strip().lower() in ("1", "true", "on", "yes")
        self.interval = _env_int("DEMO_INTERVAL_SECONDS", 120, self.MIN_INTERVAL, 3600)
        self.hold = _env_int("DEMO_READINESS_HOLD_SECONDS", 40, 25, 300)
        self.next_at = time.time() + 30          # first injection ~30 s after the dashboard starts
        self.force_once = False
        self.next_kind = "liveness"
        self.active = None
        self.history = []
        self.injected_total = 0
        self.recovered_total = 0
        self.last_skip = None

    # ---- helpers
    def _unsafe_reason(self, pods, dep):
        if dep["startup_delay"] > 0:
            return "slow start-up scenario is active"
        if dep["desired"] < 2:
            return "needs at least 2 replicas"
        if dep["total"] != dep["desired"] or dep["updated"] != dep["desired"]:
            return "a rollout is in progress"
        if len(pods) != dep["desired"]:
            return "waiting for all pods to exist"
        for p in pods:
            if p["terminating"] or not p["healthy"]:
                return f"waiting for {p['name']} to become healthy"
            a = p.get("app") or {}
            if a.get("liveness_failure_injected") or a.get("readiness_failure_injected"):
                return "another failure is already active"
        return None

    def _finish(self, now, outcome):
        ev = self.active
        ev["outcome"], ev["finished_at"] = outcome, now
        ev["detect_seconds"] = None if ev["detected_at"] is None else round(ev["detected_at"] - ev["injected_at"], 1)
        ev["recover_seconds"] = None if ev["recovered_at"] is None else round(ev["recovered_at"] - ev["injected_at"], 1)
        if outcome == "recovered":
            self.recovered_total += 1
        self.history.insert(0, ev)
        del self.history[12:]
        self.active = None
        self.next_at = now + self.interval

    # ---- one scheduler step (called every ~2 s by the background thread)
    def tick(self, now=None):
        now = time.time() if now is None else now
        with self.lock:
            active, due = self.active, (self.enabled or self.force_once) and now >= self.next_at
        if active:
            return self._progress(now)
        if due:
            return self._try_inject(now)

    def _try_inject(self, now):
        try:
            pods = [p for p in get_pods() if not p["terminating"]]
            dep = get_deployment()
            with self.lock:
                reason = self._unsafe_reason(pods, dep)
                if reason:
                    self.last_skip = {"reason": reason, "at": now}
                    self.next_at = now + 10          # look again soon
                    return
                kind = self.next_kind
                pod = random.choice(pods)
                duration = self.LIVENESS_EXPIRY if kind == "liveness" else self.hold
                pod_call(pod["ip"], f"/control/{kind}", "POST", {"fail": True, "duration_seconds": duration}, timeout=3)
                self.next_kind = "readiness" if kind == "liveness" else "liveness"
                self.injected_total += 1
                self.force_once, self.last_skip = False, None
                self.active = {"n": self.injected_total, "kind": kind, "pod": pod["name"], "injected_at": now,
                               "restarts_before": pod["restarts"], "detected_at": None, "recovered_at": None,
                               "clear_at": now + self.hold if kind == "readiness" else None, "cleared": False,
                               "state": "injected", "outcome": None}
                print(f"demo: injected {kind} failure into {pod['name']}", flush=True)
        except Exception as e:                       # API/pod hiccup: never crash the loop
            with self.lock:
                self.last_skip = {"reason": f"could not inject: {e}", "at": now}
                self.next_at = now + 15

    def _progress(self, now):
        try:
            pods = {p["name"]: p for p in get_pods()}
        except Exception:
            return
        with self.lock:
            ev = self.active
            if ev is None:
                return
            p = pods.get(ev["pod"])
            if p is None or p["terminating"]:
                return self._finish(now, "aborted (pod was replaced)")
            a = p.get("app") or {}
            if ev["kind"] == "liveness":
                if ev["detected_at"] is None and (p["restarts"] > ev["restarts_before"] or p["liveness"]["state"] == "Failing"):
                    ev["detected_at"], ev["state"] = now, "detected - Kubernetes is restarting the container"
                if p["restarts"] > ev["restarts_before"] and p["healthy"] and not a.get("liveness_failure_injected"):
                    ev["recovered_at"], ev["state"] = now, "recovered"
                    return self._finish(now, "recovered")
                timeout = self.LIVENESS_EXPIRY + 45
            else:
                if ev["detected_at"] is None and not p["ready"]:
                    ev["detected_at"], ev["state"] = now, "detected - pod removed from the Service endpoints"
                if now >= ev["clear_at"] and not ev["cleared"]:
                    try:
                        pod_call(p["ip"], "/control/reset", "POST", {}, timeout=3)
                        ev["cleared"], ev["state"] = True, "failure cleared - waiting for readiness probe to pass"
                    except Exception:
                        pass                        # the app also self-clears at the expiry
                if p["healthy"] and not a.get("readiness_failure_injected") and ev["detected_at"] is not None and now >= ev["clear_at"]:
                    ev["recovered_at"], ev["state"] = now, "recovered"
                    return self._finish(now, "recovered")
                timeout = self.hold + 60
            if now - ev["injected_at"] > timeout:                 # safety net: never leave a failure behind
                try:
                    if p["ip"]:
                        pod_call(p["ip"], "/control/reset", "POST", {}, timeout=3)
                except Exception:
                    pass
                self._finish(now, "timed out - failure force-cleared")

    # ---- API
    def configure(self, enabled=None, interval=None):
        with self.lock:
            if interval is not None:
                if isinstance(interval, bool) or not isinstance(interval, int) or not self.MIN_INTERVAL <= interval <= 3600:
                    raise ValueError(f"interval must be a whole number between {self.MIN_INTERVAL} and 3600 seconds")
                self.interval = interval
                self.next_at = min(self.next_at, time.time() + interval) if self.active is None else self.next_at
            if enabled is not None:
                self.enabled = bool(enabled)
                if self.enabled and self.active is None:
                    self.next_at = time.time() + min(self.interval, 20)

    def run_now(self):
        with self.lock:
            self.force_once, self.next_at = True, time.time()

    def snapshot(self):
        now = time.time()
        with self.lock:
            return {"enabled": self.enabled, "interval_seconds": self.interval, "readiness_hold_seconds": self.hold,
                    "next_in_seconds": None if (not self.enabled and not self.force_once) else max(0, int(self.next_at - now)),
                    "next_kind": self.next_kind, "active": None if not self.active else {**self.active, "age_seconds": max(0, int(now - self.active["injected_at"]))},
                    "history": [{**h, "ago_seconds": max(0, int(now - h["finished_at"]))} for h in self.history],
                    "injected_total": self.injected_total, "recovered_total": self.recovered_total,
                    "last_skip": None if not self.last_skip else {"reason": self.last_skip["reason"], "ago_seconds": int(now - self.last_skip["at"])}}


DEMO = DemoMode()


def demo_loop():
    while True:
        try:
            DEMO.tick()
        except Exception as e:
            print(f"demo loop error: {e}", flush=True)
        time.sleep(2)


@app.get("/api/demo")
def demo_status():
    return jsonify(DEMO.snapshot())


@app.post("/api/demo")
def demo_config():
    body = request.get_json(silent=True) or {}
    try:
        DEMO.configure(enabled=body.get("enabled"), interval=body.get("interval"))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(DEMO.snapshot())


@app.post("/api/demo/run-now")
def demo_run_now():
    DEMO.run_now()
    return jsonify(ok=True, message="Demo failure scheduled. It is injected within ~2 s if every pod is healthy.",
                   demo=DEMO.snapshot())

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
    dbs = [p["database"] for p in live_pods if p.get("database")]
    student_app = {"name": "Student Management", "image": dep.get("image"),
                   "students": next((d["students"] for d in dbs if d.get("ok") and d.get("students") is not None), None),
                   "database_ok_pods": sum(1 for d in dbs if d.get("ok")), "database_pods_reporting": len(dbs),
                   "database_path": next((d.get("path") for d in dbs), None)}
    return jsonify(
        time=datetime.now(timezone.utc).isoformat(), namespace=NAMESPACE, student_app=student_app, demo=DEMO.snapshot(),
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
    print(f"dashboard: namespace={NAMESPACE} deployment={DEPLOYMENT} service={SERVICE} "
          f"demo_mode={'on' if DEMO.enabled else 'off'} every {DEMO.interval}s", flush=True)
    threading.Thread(target=demo_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, threaded=True)
