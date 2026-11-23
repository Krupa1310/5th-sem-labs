"""
Health-check demo application  (Cloud Computing 26ECAC301 - Problem 14)

A tiny Flask app that Kubernetes probes. It exposes:

  GET  /healthz   LIVENESS endpoint.  200 normally, 500 after failure is injected.
  GET  /ready     READINESS endpoint. 200 when ready, 503 while starting up or
                  after readiness failure is injected.
  GET  /whoami    Which pod answered?  (used to prove the Service skips NotReady pods)
  GET  /info      Full state of this pod (used by the dashboard).
  GET  /startupz  STARTUP endpoint.   200 once the database is initialised, else 503.

Student Management (ordinary business endpoints - see students.py, kept separate
from the health endpoints above):

  GET    /                  web UI (HTML)
  GET    /api/students?q=   list / search
  POST   /api/students      add          GET/PUT/DELETE /api/students/<id>

  POST /control/liveness    {"fail": true|false, "duration_seconds": N?}  make /healthz return 500 / 200
  POST /control/readiness   {"fail": true|false, "duration_seconds": N?}  make /ready  return 503 / 200
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

from flask import Flask, jsonify, request, send_from_directory

import students

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.register_blueprint(students.bp)

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
# Optional expiry (epoch seconds) of an injected failure. The automatic demo mode always sets one, so
# a pod can never stay broken forever, even if the dashboard that injected the failure disappears.
flag_until = {"liveness_fail": None, "readiness_fail": None}
# The last probe request that came from the *kubelet* (identified by its User-Agent)
last_probe = {"liveness": None, "readiness": None, "startup": None}
probe_count = {"liveness": {"ok": 0, "fail": 0}, "readiness": {"ok": 0, "fail": 0},
               "startup": {"ok": 0, "fail": 0}}
# Database initialisation state (set by init_database_with_retry)
db_state = {"initialised": False, "error": None}


def log(msg):
    print(f"[{POD_NAME}] {msg}", flush=True)


def failing(name):
    """Is this injected failure currently active? (clears itself once its expiry has passed)"""
    with _lock:
        until = flag_until.get(name)
        if flags[name] and until is not None and time.time() >= until:
            flags[name], flag_until[name] = False, None
            log(f"{name} FAILURE EXPIRED (auto-cleared)")
        return flags[name]


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


def init_database_with_retry(attempts=30, delay=2.0):
    """Create the SQLite file/table. Runs in a background thread so the process is
    already answering /healthz (liveness) while it is still preparing the database;
    /startupz and /ready stay 503 until it is done."""
    for i in range(1, attempts + 1):
        try:
            students.init_db()
            db_state["initialised"], db_state["error"] = True, None
            log(f"database ready at {students.db_path()}")
            return
        except Exception as e:  # sqlite3.Error, OSError (volume not writable) ...
            db_state["error"] = str(e)
            log(f"database init attempt {i}/{attempts} failed: {e}")
            time.sleep(delay)


@app.after_request
def add_pod_header(resp):
    resp.headers["X-Served-By"] = POD_NAME      # lets the UI show which pod answered
    return resp


# ----------------------------------------------------------------- probes
@app.get("/startupz")
def startupz():
    """Startup: 'has the application finished starting up?' (database initialised)."""
    if not db_state["initialised"]:
        record_probe("startup", 503)
        return jsonify(started=False, reason=db_state["error"] or "initialising database", pod=POD_NAME), 503
    record_probe("startup", 200)
    return jsonify(started=True, pod=POD_NAME), 200


@app.get("/healthz")
def healthz():
    """Liveness: 'is the process still working?'"""
    if failing("liveness_fail"):
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
    if failing("readiness_fail"):
        record_probe("readiness", 503)
        return jsonify(ready=False, reason="readiness failure injected", pod=POD_NAME), 503
    db_ok, db_err = students.check_db() if db_state["initialised"] else (False, "database not initialised yet")
    if not db_ok:
        record_probe("readiness", 503)
        return jsonify(ready=False, reason=f"database unavailable: {db_err}", pod=POD_NAME), 503
    record_probe("readiness", 200)
    return jsonify(ready=True, pod=POD_NAME), 200


# ------------------------------------------------------------ information
@app.get("/whoami")
def whoami():
    return jsonify(pod=POD_NAME, ip=POD_IP)


@app.get("/")
@app.get("/students")
def student_ui():
    """Student Management web UI (static HTML; talks to /api/students)."""
    return send_from_directory(app.static_folder, "index.html")


@app.get("/info")
def info():
    now = time.time()
    with _lock:
        probes = {
            kind: (None if p is None else {"status": p["status"], "age_seconds": round(now - p["time"], 1)})
            for kind, p in last_probe.items()
        }
        counts = {k: dict(v) for k, v in probe_count.items()}
    db_ok, db_err = students.check_db() if db_state["initialised"] else (False, db_state["error"] or "initialising")
    return jsonify(
        pod=POD_NAME,
        ip=POD_IP,
        uptime_seconds=round(now - START_TIME, 1),
        startup_delay_seconds=STARTUP_DELAY,
        startup_remaining_seconds=startup_remaining(),
        liveness_failure_injected=failing("liveness_fail"),
        readiness_failure_injected=failing("readiness_fail"),
        healthz_status=500 if failing("liveness_fail") else 200,
        ready_status=200 if (startup_remaining() == 0 and not failing("readiness_fail") and db_ok) else 503,
        database={"ok": db_ok, "error": db_err, "initialised": db_state["initialised"],
                  "path": students.db_path(), "students": students.count_students() if db_ok else None},
        last_kubelet_probe=probes,
        kubelet_probe_counts=counts,
    )


# ------------------------------------------------------------ JSON errors
@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not found."), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify(error="Method not allowed."), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify(error="Internal server error."), 500


# ---------------------------------------------------------------- controls
def _set_flag(name, label):
    """Body (all optional): {"fail": true|false, "duration_seconds": N}.
    Without duration_seconds the failure lasts until reset/restart (original behaviour)."""
    body = request.get_json(silent=True) or {}
    value = bool(body.get("fail", True))
    until = None
    if value and body.get("duration_seconds") is not None:
        try:
            until = time.time() + max(1, min(int(body["duration_seconds"]), 600))
        except (TypeError, ValueError):
            return jsonify(error="duration_seconds must be a whole number of seconds"), 400
    with _lock:
        flags[name] = value
        flag_until[name] = until if value else None
    log(f"{label} FAILURE {'INJECTED' if value else 'CLEARED'}" + (f" (auto-clears in {int(until - time.time())}s)" if until else ""))
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
        flag_until["liveness_fail"] = flag_until["readiness_fail"] = None
    log("ALL FAILURES CLEARED")
    return jsonify(pod=POD_NAME, **flags)


def _graceful_exit(signum, frame):
    # Python as PID 1 ignores SIGTERM by default, which would make every pod
    # take 30 s to terminate. Exit immediately instead.
    log("SIGTERM received, shutting down")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _graceful_exit)
    log(f"starting on :5000 (startup delay = {STARTUP_DELAY}s, db = {students.db_path()})")
    threading.Thread(target=init_database_with_retry, daemon=True).start()
    # threaded=True: probes and user requests are served concurrently.
    # (Flask's built-in server is fine for a lab; use gunicorn for production.)
    app.run(host="0.0.0.0", port=5000, threaded=True)
