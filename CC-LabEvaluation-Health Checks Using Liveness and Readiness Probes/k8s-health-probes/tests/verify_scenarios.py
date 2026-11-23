#!/usr/bin/env python3
"""
End-to-end verification of the three lab scenarios, using ONLY kubectl.
(It does not use the dashboard, so it is an independent check of real cluster behaviour.)

    python tests/verify_scenarios.py            # run all three scenarios
    python tests/verify_scenarios.py liveness   # or: readiness | slowstart

Every check prints PASS / FAIL with the evidence it saw. Exit code 0 = all passed.
Takes ~3-4 minutes in total (slow start-up alone is ~1 minute).
"""
import json
import subprocess
import sys
import time

LABEL = "app=health-demo"
SVC = "health-demo-svc"
results = []


def kubectl(*args, check=True):
    r = subprocess.run(["kubectl", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"kubectl {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def pods():
    items = json.loads(kubectl("get", "pods", "-l", LABEL, "-o", "json"))["items"]
    out = []
    for p in items:
        if p["metadata"].get("deletionTimestamp"):
            continue
        cs = p["status"].get("containerStatuses", [{}])[0]
        out.append({"name": p["metadata"]["name"], "ip": p["status"].get("podIP"), "phase": p["status"].get("phase"),
                    "ready": cs.get("ready", False), "restarts": cs.get("restartCount", 0)})
    return sorted(out, key=lambda x: x["name"])


def get_pod(name):
    return next((p for p in pods() if p["name"] == name), None)


def endpoints():
    ep = json.loads(kubectl("get", "endpoints", SVC, "-o", "json"))
    ready, notready = set(), set()
    for s in ep.get("subsets") or []:
        ready |= {a["ip"] for a in s.get("addresses") or []}
        notready |= {a["ip"] for a in s.get("notReadyAddresses") or []}
    return ready, notready


def wait(cond, timeout, what, every=2):
    end = time.time() + timeout
    while time.time() < end:
        v = cond()
        if v:
            return v
        time.sleep(every)
    return None


def check(ok, msg, evidence=""):
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {msg}" + (f"   <- {evidence}" if evidence else ""))
    return ok


def show():
    print(kubectl("get", "pods", "-l", LABEL).rstrip().replace("\n", "\n      "), flush=True)


def exec_app(pod, path, method="POST"):
    code = ("import urllib.request as u;"
            f"print(u.urlopen(u.Request('http://localhost:5000{path}',data=b'{{}}',method='{method}',"
            "headers={'Content-Type':'application/json'})).read().decode())")
    return kubectl("exec", pod, "--", "python", "-c", code)


def service_hits(n=30):
    """Send n requests through the Service from inside the cluster; return {pod: count}."""
    code = ("import urllib.request as u,json,collections;c=collections.Counter()\n"
            f"for _ in range({n}):\n"
            f"  try: c[json.load(u.urlopen('http://{SVC}/whoami',timeout=2))['pod']]+=1\n"
            "  except Exception: c['ERROR']+=1\n"
            "print(json.dumps(c))")
    return json.loads(kubectl("exec", "deploy/health-dashboard", "--", "python", "-c", code))


def events_for(pod):
    return kubectl("get", "events", "--field-selector", f"involvedObject.name={pod}",
                   "-o", "custom-columns=REASON:.reason,MESSAGE:.message", "--no-headers")


def preflight():
    print("== Pre-flight: all pods Running, 1/1 Ready, all IPs in Service endpoints")
    ps = wait(lambda: (lambda x: x if len(x) == 3 and all(p["ready"] for p in x) else None)(pods()), 120, "healthy")
    check(ps is not None, "3 pods are Running and 1/1 Ready")
    if not ps:
        sys.exit("Deployment is not healthy - run scripts/deploy.sh first.")
    ready, _ = endpoints()
    check(ready == {p["ip"] for p in ps}, "Service endpoints list every pod IP", ", ".join(sorted(ready)))
    show()


# --------------------------------------------------------------- scenarios
def scenario_liveness():
    print("\n== Scenario A: LIVENESS failure")
    target = pods()[0]
    name, r0 = target["name"], target["restarts"]
    print(f"  target pod: {name}   restarts before: {r0}")
    exec_app(name, "/control/liveness")
    print("  injected: /healthz now returns 500 (kubelet needs 3 failures x 5 s = ~15 s)")
    restarted = wait(lambda: (get_pod(name) or {}).get("restarts", 0) > r0, 90, "restart")
    check(bool(restarted), "kubelet restarted the container automatically")
    ev = events_for(name)
    check("Liveness probe failed" in ev, "describe/events show 'Liveness probe failed'",
          next((l for l in ev.splitlines() if "Liveness probe failed" in l), "").strip()[:90])
    check("failed liveness probe, will be restarted" in ev, "events show the container being killed for restart")
    rec = wait(lambda: (lambda p: p if p and p["ready"] and p["phase"] == "Running" else None)(get_pod(name)), 90, "recover")
    check(bool(rec), "pod recovered: Running and 1/1 Ready again")
    if rec:
        check(rec["restarts"] == r0 + 1, "restart count increased by exactly 1", f"{r0} -> {rec['restarts']}")
        ready, _ = endpoints()
        check(rec["ip"] in ready, "pod IP is back in the Service endpoints")
    show()


def scenario_readiness():
    print("\n== Scenario B: READINESS failure")
    ps = pods()
    target, others = ps[0], ps[1:]
    name, ip, r0 = target["name"], target["ip"], target["restarts"]
    print(f"  target pod: {name} ({ip})   restarts before: {r0}")
    exec_app(name, "/control/readiness")
    print("  injected: /ready now returns 503")
    nr = wait(lambda: (lambda p: p if p and not p["ready"] else None)(get_pod(name)), 60, "notready")
    check(bool(nr), "READY changed 1/1 -> 0/1")
    time.sleep(1)
    p = get_pod(name)
    check(p["phase"] == "Running", "pod is still Running", p["phase"])
    check(p["restarts"] == r0, "restart count did NOT increase", f"{r0} -> {p['restarts']}")
    ready, notready = endpoints()
    check(ip not in ready, "pod IP removed from Service endpoints (ready list)", f"ready={sorted(ready)}")
    hits = service_hits(30)
    check(name not in hits and "ERROR" not in hits, "30 requests via the Service: none reached the NotReady pod", str(hits))
    show()
    print("  restoring readiness ...")
    exec_app(name, "/control/reset")
    back = wait(lambda: (lambda p: p if p and p["ready"] else None)(get_pod(name)), 60, "ready again")
    check(bool(back), "READY returned to 1/1")
    ready, _ = endpoints()
    check(ip in ready, "pod IP added back to Service endpoints")
    check(get_pod(name)["restarts"] == r0, "restart count still unchanged", str(get_pod(name)["restarts"]))
    show()


def scenario_slowstart():
    print("\n== Scenario C: SLOW START-UP (30 s)")
    old = {p["name"] for p in pods()}
    kubectl("set", "env", "deployment/health-demo", "STARTUP_DELAY_SECONDS=30")
    print("  patched Deployment: STARTUP_DELAY_SECONDS=30  -> rolling update begins")
    def new_unready():
        n = [p for p in pods() if p["name"] not in old and p["phase"] == "Running" and not p["ready"]]
        return n or None
    nu = wait(new_unready, 60, "new pod running notready", every=1)
    check(bool(nu), "a NEW pod is Running but NotReady (0/1) while initialising")
    if nu:
        p = nu[0]
        ready, notready = endpoints()
        check(p["ip"] not in ready, "NotReady pod is not in the Service's ready endpoints", f"ip={p['ip']}")
        check(p["restarts"] == 0, "no restarts while starting slowly (liveness stays happy)")
        show()
        hits = service_hits(30)
        check(not any(n["name"] in hits for n in nu), "30 requests via the Service: none sent to the initialising pods", str(hits))
        check("ERROR" not in hits, "no failed requests during the rollout (old pods keep serving)")
    done = wait(lambda: (lambda x: x if len(x) == 3 and all(p["ready"] for p in x) and not (old & {p["name"] for p in x}) else None)(pods()),
                150, "rollout complete", every=3)
    check(bool(done), "after ~30 s all new pods became 1/1 Ready")
    if done:
        ready, _ = endpoints()
        check(ready == {p["ip"] for p in done}, "all new pod IPs are now in the Service endpoints")
    show()
    print("  restoring: STARTUP_DELAY_SECONDS=0 ...")
    kubectl("set", "env", "deployment/health-demo", "STARTUP_DELAY_SECONDS=0")
    kubectl("rollout", "status", "deployment/health-demo", "--timeout=120s")


if __name__ == "__main__":
    which = sys.argv[1:] or ["liveness", "readiness", "slowstart"]
    preflight()
    for w in which:
        {"liveness": scenario_liveness, "readiness": scenario_readiness, "slowstart": scenario_slowstart}[w]()
    print(f"\n==== {sum(results)}/{len(results)} checks passed ====")
    sys.exit(0 if all(results) else 1)
