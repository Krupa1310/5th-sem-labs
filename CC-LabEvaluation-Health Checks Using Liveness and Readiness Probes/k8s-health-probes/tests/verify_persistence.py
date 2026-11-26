#!/usr/bin/env python3
"""
Cluster test: do student records survive pod and container restarts?   (needs the app deployed)

    python tests/verify_persistence.py                    # uses http://localhost:30080
    python tests/verify_persistence.py http://localhost:30080

A: delete ONE pod            -> record still there
B: delete ALL app pods       -> record still there (new pods mount the same volume)
C: liveness failure          -> kubelet restarts the container -> record still there
The test record is removed at the end. Exit code 0 = all passed.
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:30080").rstrip("/")
LABEL, REPLICAS = "app=health-demo", 3
failures = []


def kubectl(*a):
    r = subprocess.run(["kubectl", *a], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"kubectl {' '.join(a)} failed: {r.stderr.strip()}")
    return r.stdout


def pods():
    items = json.loads(kubectl("get", "pods", "-l", LABEL, "-o", "json"))["items"]
    out = []
    for p in items:
        if p["metadata"].get("deletionTimestamp"):
            continue
        cs = (p["status"].get("containerStatuses") or [{}])[0]
        out.append({"name": p["metadata"]["name"], "ready": bool(cs.get("ready")), "restarts": cs.get("restartCount", 0)})
    return out


def wait(cond, timeout, what):
    end = time.time() + timeout
    while time.time() < end:
        v = cond()
        if v:
            return v
        time.sleep(2)
    sys.exit(f"TIMEOUT waiting for: {what}")


def all_ready():
    p = pods()
    return p if len(p) == REPLICAS and all(x["ready"] for x in p) else None


def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def find(student_id):
    for _ in range(15):                       # the Service may briefly route to a terminating pod
        try:
            return [s for s in api("GET", "/api/students?q=" + urllib.parse.quote(student_id))["students"] if s["student_id"] == student_id]
        except (urllib.error.URLError, OSError):
            time.sleep(2)
    return []


def check(ok, msg):
    print(f"  [{'PASS' if ok else 'FAIL'}] {msg}")
    if not ok:
        failures.append(msg)


print(f"Target: {BASE}")
wait(all_ready, 120, "3 ready pods")
sid = "PERSIST" + str(int(time.time()))[-6:]
rec = api("POST", "/api/students", {"student_id": sid, "name": "Persistence Test", "email": f"{sid.lower()}@example.com",
                                    "department": "Test", "semester": 1})
print(f"Created test record {sid} (row id {rec['id']})")

print("\nA: delete ONE pod")
victim = pods()[0]["name"]
kubectl("delete", "pod", victim, "--wait=false")
wait(all_ready, 120, "3 ready pods after deleting one")
check(len(find(sid)) == 1, f"record present after deleting {victim}")

print("\nB: delete ALL application pods")
kubectl("delete", "pods", "-l", LABEL, "--wait=false")
time.sleep(5)
wait(all_ready, 180, "3 ready pods after deleting all")
check(len(find(sid)) == 1, "record present after ALL pods were recreated")

print("\nC: liveness failure -> container restart")
target = pods()[0]
kubectl("exec", target["name"], "--", "python", "-c",
        "import urllib.request as u;u.urlopen(u.Request('http://localhost:5000/control/liveness',data=b'{}',method='POST',"
        "headers={'Content-Type':'application/json'}))")
restarted = wait(lambda: next((p for p in pods() if p["name"] == target["name"] and p["restarts"] > target["restarts"] and p["ready"]), None),
                 120, "container restart")
check(True, f"kubelet restarted the container in {target['name']} (restarts {target['restarts']} -> {restarted['restarts']})")
check(len(find(sid)) == 1, "record present after the container restart")

api("DELETE", f"/api/students/{rec['id']}")
print("\nTest record removed.")
print("ALL PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED")
sys.exit(1 if failures else 0)
