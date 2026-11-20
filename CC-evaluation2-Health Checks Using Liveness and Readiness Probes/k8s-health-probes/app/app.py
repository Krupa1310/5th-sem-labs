"""
Health-check demo application  (Cloud Computing 26ECAC301 - Problem 14)

A tiny Flask app that Kubernetes probes. It exposes:

  GET  /healthz   LIVENESS endpoint.  200 normally, 500 after failure is injected.
  GET  /ready     READINESS endpoint. 200 when ready, 503 while starting up or
                  after readiness failure is injected.
  GET  /whoami    Which pod answered?  (used to prove the Service skips NotReady pods)
  GET  /info      Full state of this pod (used by the dashboard).

  POST /control/liveness    {"fail": true|false}   make /healthz return 500 / 200
  POST /control/readiness   {"fail": true|false}   make /ready  return 503 / 200
  POST /control/reset                              clear every injected failure
  POST /crash                                      alias for liveness failure
                                                   (mentioned in the lab slides)

Slow start-up is configured with the STARTUP_DELAY_SECONDS environment variable.
While the process is younger than that, /ready answers 503 (but /healthz stays
200, so the liveness probe does NOT kill an app that is merely still booting).

All failure flags live in memory only. A container restart therefore starts a
fresh process with a clean state - which is exactly how "recovery" happens
after a liveness failure.
"""
import os
import signal
import socket
import sys
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

POD_NAME = os.getenv("POD_NAME", socket.gethostname())
POD_IP = os.getenv("POD_IP", "unknown")
START_TIME = time.time()

try:
    STARTUP_DELAY = max(0, int(os.getenv("STARTUP_DELAY_SECONDS", "0")))
except ValueError:
    STARTUP_DELAY = 0

_lock = threading.Lock()
# Failure switches (in memory, per container)
flags = {"liveness_fail": False, "readiness_fail": False}
# The last probe request that came from the *kubelet* (identified by its User-Agent)
last_probe = {"liveness": None, "readiness": None}
probe_count = {"liveness": {"ok": 0, "fail": 0}, "readiness": {"ok": 0, "fail": 0}}


def log(msg):
    print(f"[{POD_NAME}] {msg}", flush=True)


def startup_remaining():
    """Seconds of simulated start-up delay still left (0 once finished)."""
    return max(0, int(round(STARTUP_DELAY - (time.time() - START_TIME))))


def record_probe(kind, status):
    """Remember kubelet probe results. Only requests whose User-Agent starts with
    'kube-probe/' count, so dashboard/curl calls never pollute the numbers."""
    if not request.headers.get("User-Agent", "").startswith("kube-probe/"):
        return
    with _lock:
        last_probe[kind] = {"status": status, "time": time.time()}
        probe_count[kind]["ok" if status < 400 else "fail"] += 1


# ----------------------------------------------------------------- probes
@app.get("/healthz")
def healthz():
    """Liveness: 'is the process still working?'"""
    if flags["liveness_fail"]:
        record_probe("liveness", 500)
        return jsonify(status="unhealthy", reason="liveness failure injected", pod=POD_NAME), 500
    record_probe("liveness", 200)
    return jsonify(status="ok", pod=POD_NAME), 200


@app.get("/ready")
def ready():
    """Readiness: 'can I serve traffic right now?'"""
    remaining = startup_remaining()
    if remaining > 0:
        record_probe("readiness", 503)
        return jsonify(ready=False, reason=f"starting up, {remaining}s remaining", pod=POD_NAME), 503
    if flags["readiness_fail"]:
        record_probe("readiness", 503)
        return jsonify(ready=False, reason="readiness failure injected", pod=POD_NAME), 503
    record_probe("readiness", 200)
    return jsonify(ready=True, pod=POD_NAME), 200


# ------------------------------------------------------------ information
@app.get("/")
@app.get("/whoami")
def whoami():
    return jsonify(pod=POD_NAME, ip=POD_IP)


@app.get("/info")
def info():
    now = time.time()
    with _lock:
        probes = {
            kind: (None if p is None else {"status": p["status"], "age_seconds": round(now - p["time"], 1)})
            for kind, p in last_probe.items()
        }
        counts = {k: dict(v) for k, v in probe_count.items()}
    return jsonify(
        pod=POD_NAME,
        ip=POD_IP,
        uptime_seconds=round(now - START_TIME, 1),
        startup_delay_seconds=STARTUP_DELAY,
        startup_remaining_seconds=startup_remaining(),
        liveness_failure_injected=flags["liveness_fail"],
        readiness_failure_injected=flags["readiness_fail"],
        healthz_status=500 if flags["liveness_fail"] else 200,
        ready_status=200 if (startup_remaining() == 0 and not flags["readiness_fail"]) else 503,
        last_kubelet_probe=probes,
        kubelet_probe_counts=counts,
    )


# ---------------------------------------------------------------- controls
def _set_flag(name, label):
    body = request.get_json(silent=True) or {}
    value = bool(body.get("fail", True))
    with _lock:
        flags[name] = value
    log(f"{label} FAILURE {'INJECTED' if value else 'CLEARED'}")
    return jsonify(pod=POD_NAME, **flags)


@app.post("/control/liveness")
def control_liveness():
    return _set_flag("liveness_fail", "LIVENESS")


@app.post("/control/readiness")
def control_readiness():
    return _set_flag("readiness_fail", "READINESS")


@app.post("/crash")
def crash():
    return _set_flag("liveness_fail", "LIVENESS")


@app.post("/control/reset")
def control_reset():
    with _lock:
        flags["liveness_fail"] = False
        flags["readiness_fail"] = False
    log("ALL FAILURES CLEARED")
    return jsonify(pod=POD_NAME, **flags)


def _graceful_exit(signum, frame):
    # Python as PID 1 ignores SIGTERM by default, which would make every pod
    # take 30 s to terminate. Exit immediately instead.
    log("SIGTERM received, shutting down")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _graceful_exit)
    log(f"starting on :5000 (startup delay = {STARTUP_DELAY}s)")
    # threaded=True: probes and user requests are served concurrently.
    # (Flask's built-in server is fine for a lab; use gunicorn for production.)
    app.run(host="0.0.0.0", port=5000, threaded=True)
