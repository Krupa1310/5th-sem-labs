# Health Checks Using Liveness and Readiness Probes — Student Management on Kubernetes

**Cloud Computing (26ECAC301) · Lab Evaluation – 2 · Problem 14**  ·  KLE Technological University

A Student Management web application running as 3 pods on Kubernetes, protected by **startup, liveness and
readiness probes**, with its records stored on a **persistent volume**, and a live **monitoring dashboard** that
shows the real cluster state — including an **automatic demonstration mode** that injects short failures by itself so
you can watch Kubernetes detect and recover from them.

| | URL |
|---|---|
| Student Management app | **http://localhost:30080** |
| Monitoring dashboard | **http://localhost:30090** |

---

## 0. What was tested, and what was not (please read)

I built this in a sandbox that has **no Docker, no Kubernetes and no PowerShell**, so be clear about the difference:

| Verified here (real runs) | **Not** verified here — you must run it once on your laptop |
|---|---|
| 44 offline unit tests pass: student CRUD, search, validation, duplicates, health endpoints, probe behaviour, dashboard logic, manifest consistency | `docker build` of the two images |
| 3 separate app processes sharing one SQLite file: 300 concurrent writes, all succeeded, no "database is locked" errors; data intact after restarting a process | `kubectl apply`, the PVC on Docker Desktop, 3 pods sharing the volume |
| Student web UI driven in headless Chromium: add, edit, delete, search, inline validation errors, duplicate detection, persistence after reload, mobile layout | The real kubelet probing the new `/startupz` + DB-aware `/ready` endpoints |
| Dashboard UI rendered in Chromium against a *simulated* cluster (pods, endpoints, probes, demo history) | Demo mode against real pods (its logic is unit-tested against a fake cluster only) |
| YAML parses; image tags, probe paths, PVC mount, selectors, RBAC cross-checked against the code | `scripts/*.ps1` (no PowerShell available here), `tests/verify_persistence.py`, `tests/verify_scenarios.py` against the new Deployment |

The original project (dashboard + 3 scenarios) was previously verified on a real k3s cluster — see
`docs/VERIFIED_RUN.md` (that run predates the student upgrade). **Do a 5-minute dry run before the evaluation.**

## 1. What changed (and what was kept)

**Kept unchanged:** deployment name `health-demo` (3 replicas), Service `health-demo-svc` (NodePort 30080),
`health-dashboard` + its Service (NodePort 30090), the dashboard's RBAC (`dashboard-rbac.yaml` is byte-for-byte
unchanged), every old endpoint (`/healthz`, `/ready`, `/whoami`, `/info`, `/control/*`, `/crash`), every dashboard
button, the rolling-update settings, `demo-cli.sh`, `verify_scenarios.py`.

**Added / changed:**

| Area | Change |
|---|---|
| `app/students.py` (new) | Student CRUD REST API + SQLite storage + validation |
| `app/static/index.html` (new) | Responsive Student Management UI (served at `/`) |
| `app/app.py` | Wires in the student API; new `/startupz`; **`/ready` now also checks the database**; failures can auto-expire (`duration_seconds`); `/` now serves the UI (`/whoami` still returns the pod name) |
| `k8s/pvc.yaml` (new) | 1 Gi volume `student-data` for the SQLite file |
| `k8s/deployment.yaml` | Image `health-demo:2.0`, volume mounted at `/data`, **startup probe added**, explicit timeouts/thresholds |
| `dashboard/server.py` + UI | Shows student count, DB status per pod, startup probe, probe configuration; **automatic demo mode** with failure/recovery history |
| `k8s/dashboard.yaml` | Image `health-dashboard:2.0`, demo-mode settings |
| `scripts/*.ps1` (new) | PowerShell deploy / status / cleanup / tests |
| `tests/` | 44 offline tests, seed script, cluster persistence test |

Image tags moved from `:1.0` to `:2.0` on purpose: Kubernetes only rolls out new pods when the pod spec changes, and
a re-built image with the *same* tag would silently keep running the old code. The old `:1.0` images are left on your machine.

## 2. Run it — exact PowerShell commands

Prerequisites: Docker Desktop running with **Kubernetes enabled** (context `docker-desktop`), Python 3.10+.

```powershell
cd k8s-health-probes                       # the project folder

# 1. check the environment
docker --version
kubectl config current-context             # must print: docker-desktop
kubectl get nodes                          # node should be Ready

# 2. build both images, create the volume, deploy the app, upgrade the dashboard in place
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1

# 3. look at the result
kubectl get pods -o wide                   # 3 x health-demo  1/1 Running, 1 x health-dashboard
kubectl get pvc student-data               # STATUS Bound
kubectl get endpoints health-demo-svc      # 3 pod IPs

# 4. (optional) add sample students
python .\tests\seed_students.py
```

Then open **http://localhost:30080** (students) and **http://localhost:30090** (dashboard).
If a NodePort isn't reachable, forward instead (one terminal each):
`kubectl port-forward svc/health-demo-svc 30080:80` and `kubectl port-forward svc/health-dashboard 30090:80`.

The deploy script never deletes anything. The dashboard is updated **in place** (same Deployment, Service and RBAC),
so there is no monitoring gap beyond the normal rolling restart.

Equivalent manual commands (what `deploy.ps1` runs):
```powershell
docker build -t health-demo:2.0 app
docker build -t health-dashboard:2.0 dashboard
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl rollout status deployment/health-demo
kubectl apply -f k8s/dashboard-rbac.yaml -f k8s/dashboard.yaml
kubectl rollout status deployment/health-dashboard
```

## 3. Testing

**Offline (no cluster):**
```powershell
pip install -r tests\requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1      # or: python -m unittest discover -s tests -p "test_*.py" -v
```
| File | Covers |
|---|---|
| `tests/test_students_api.py` | add / list / get / update / delete, search, validation, duplicates, SQL-injection safety, persistence across a "restart", JSON errors, DB-down → 503 |
| `tests/test_health_endpoints.py` | `/healthz`, `/ready`, `/startupz`, failure injection & auto-expiry, readiness fails when DB is unreachable while liveness stays OK, health routes separate from CRUD |
| `tests/test_dashboard_demo.py` | dashboard aggregation, demo-mode safety rules, injection, detection and recovery tracking (fake cluster) |
| `tests/test_manifests.py` | image names, probe paths vs. real Flask routes, PVC mount, selectors, RBAC, no credentials in YAML |

**Against the cluster (after deploying).** Pause the automatic demo mode first, otherwise it may inject a failure in the
middle of a test and skew the restart counts:
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:30090/api/demo" -ContentType "application/json" -Body '{"enabled":false}'
python .\tests\verify_persistence.py       # deletes one pod, then all pods, then forces a restart: record must survive each (~3-4 min)
python .\tests\verify_scenarios.py         # original 3 probe scenarios, kubectl only (~4 min)
```
Re-enable it afterwards by ticking the box on the dashboard (or `-Body '{"enabled":true}'`).

## 4. Demonstration procedure (what to show the evaluator)

Open three things side by side: the **dashboard**, the **student app**, and a PowerShell window:
```powershell
kubectl get pods -l app=health-demo -w
```

**Part 1 — the app and its data (1 min).** In the student app add two students, edit one, search, delete one. Note the
**pod: …** badge (top right) changes between requests as the Service load-balances over 3 pods. The dashboard's
**Student records** card shows the same count.

**Part 2 — automatic failure and recovery (about 3 min, hands-off).** Do nothing; the *Automatic demonstration mode*
panel on the dashboard injects one failure at a time, alternating:
1. **Liveness failure (first, ~30 s after the dashboard starts).** One pod's `/healthz` starts returning 500.
   The pod's *Liveness probe* column turns **Failing**; after 3 failed probes (~15 s) Kubernetes kills and restarts the
   container: **Restarts 0 → 1**, events show `Liveness probe failed` and `Killing`, the pod returns to `1/1`.
   The history table records *detected after / recovered after*.
2. **Readiness failure (next, ~2 min later).** One pod's `/ready` returns 503. After ~15 s the pod goes `0/1`
   (still `Running`, **Restarts unchanged**), its IP moves to *NotReady* in *Service endpoints*, and "Send 30 requests"
   shows it receives **0** requests. After ~40 s the failure is cleared and the pod rejoins.
3. Throughout, the student app keeps working through the other two pods — refresh it, add a record.

Use **Inject now** to skip the wait, and the checkbox/interval to pause or change the schedule.

**Part 3 — data survives restarts (1 min).**
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:30080/api/students" -ContentType "application/json" `
  -Body '{"student_id":"DEMO001","name":"Demo Student","email":"demo@example.com","department":"CSE","semester":4}'
kubectl delete pods -l app=health-demo         # destroy ALL application pods
kubectl get pods -l app=health-demo -w         # new pods appear, 0/1 -> 1/1
(Invoke-RestMethod "http://localhost:30080/api/students?q=DEMO001").students     # the record is still there
```

**Part 4 (optional) — the original manual scenarios.** The dashboard buttons *Trigger Liveness Failure*, *Trigger
Readiness Failure*, *Simulate Slow Startup* and *Restore* still work exactly as before (see `docs/ARCHITECTURE.md`).

### Is demo mode safe?
* One failure at a time; starts only when **every pod is healthy**, no other failure is active, and no rollout is running.
* Every injected failure **expires inside the app itself** (readiness 40 s, liveness 75 s) — even if the dashboard
  crashed, nothing stays broken. Anything not recovered after a timeout is force-cleared.
* It never touches the database, so no student data can be lost. Interval is ≥ 45 s (default 120 s).
* It is **on by default** (`DEMO_MODE: "on"` in `k8s/dashboard.yaml`). To start paused, set it to `"off"` and
  `kubectl apply -f k8s/dashboard.yaml`; you can also untick it in the dashboard at any time.

## 5. Architecture and how the probes work (for the evaluation)

```
Browser ──▶ Service health-demo-svc (NodePort 30080) ──▶ only READY pods ──▶ 3 × Student app pod (Flask :5000)
                                                                              │   reads/writes
                                                                              ▼
                                                          PersistentVolumeClaim student-data ──▶ /data/students.db (SQLite)
kubelet ──▶ GET /startupz  (startup)    every 2 s, up to 60 s      ┐
        ──▶ GET /healthz   (liveness)   every 5 s, 3 failures      ├─ on each pod
        ──▶ GET /ready     (readiness)  every 5 s, 3 failures      ┘
Browser ──▶ Service health-dashboard (30090) ──▶ Dashboard pod ──▶ Kubernetes API (pods, endpoints, events, deployment)
                                                              └──▶ each app pod's IP: /info, /control/*   (+ demo-mode scheduler)
```

| Probe | Question | Endpoint | If it fails |
|---|---|---|---|
| **Startup** | Has the app finished starting (database ready)? | `/startupz` | Container restarted after 60 s; liveness/readiness wait until it passes |
| **Liveness** | Is the process still working? | `/healthz` (cheap, **does not touch the database**) | Container **restarted** after 3 failures (~15 s) |
| **Readiness** | Can this pod serve students *right now*? | `/ready` (checks the database, start-up delay, injected failure) | Pod **removed from the Service endpoints**, **no restart** |

Design points worth saying out loud:
* **Health endpoints are separate from business endpoints** (`/healthz`, `/ready`, `/startupz` vs `/api/students…`); a CRUD bug cannot make a pod look healthy or sick, and the probes never create load on student data.
* **Liveness doesn't check the database; readiness does.** If the database is briefly unreachable, restarting every pod would not fix it — it would only cause an outage. Instead the pods are taken out of rotation until the database is back.
* The **startup probe** gives slow boots up to 60 s without making the liveness probe tolerant of real hangs later (liveness stays at ~15 s).
* The dashboard **observes, it does not decide**: pod status, restarts, endpoints and events come from the Kubernetes API; probe results come from the real kubelet requests (identified by `User-Agent: kube-probe/…`) as recorded by the app.
* Persistence: records live on the PVC, not in the container, so they survive restarts, rollouts and pod deletion.

## 6. Student Management API

| Method & path | Purpose |
|---|---|
| `GET /` | Web UI |
| `GET /api/students?q=text` | List all / search by ID, name, email, department or semester |
| `POST /api/students` | Add `{student_id, name, email, department, semester(1-8)}` → 201 |
| `GET /api/students/<id>` | One student (`<id>` = internal row id) |
| `PUT /api/students/<id>` | Update (any subset of the fields) |
| `DELETE /api/students/<id>` | Delete |

Errors are JSON: `400` validation (with per-field messages), `404` not found, `409` duplicate Student ID/email, `503` database unavailable.

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `deploy.ps1` stops: wrong context | `kubectl config use-context docker-desktop` |
| Pods `ErrImagePull` / `ErrImageNeverPull` | The cluster can't see the local image. In Docker Desktop → Settings → Kubernetes use the *kubeadm* cluster type, or enable "Use containerd for pulling and storing images", then `kubectl rollout restart deployment/health-demo deployment/health-dashboard` |
| Pods `Pending`, PVC `Pending` | `kubectl describe pvc student-data`; `kubectl get storageclass` should show a default class (Docker Desktop: `hostpath`) |
| Pods stay `0/1` | `kubectl describe pod <name>` (probe events) and `kubectl logs <name>`; `/ready` says why in its JSON (`database unavailable…`) |
| App reachable but "database is temporarily unavailable" | `kubectl exec <pod> -- ls -l /data`; check the PVC is Bound |
| `localhost:30080` not reachable | Use the `kubectl port-forward` commands in §2 |
| Dashboard says "Cannot load cluster data" | `kubectl logs deploy/health-dashboard`; `kubectl get role,rolebinding health-dashboard` |
| Demo mode never injects | The panel says why (e.g. "waiting for … to become healthy"); it only runs when all 3 pods are healthy |
| Want to stop automatic failures | Untick the box on the dashboard, or set `DEMO_MODE: "off"` in `k8s/dashboard.yaml` and re-apply |
| Start over **keeping** data / **wiping** data | `.\scripts\cleanup.ps1` / `.\scripts\cleanup.ps1 -Purge` |

## 8. Known limitations (honest list)
* **SQLite on a ReadWriteOnce volume** is appropriate for a single-node local cluster (Docker Desktop): all 3 pods are on one node and share the file; writes are serialised with `BEGIN IMMEDIATE` and a busy timeout. On a multi-node cluster use a real database (MySQL/PostgreSQL) or a ReadWriteMany volume.
* Flask's built-in server is used (fine for a lab); production would use gunicorn.
* No authentication on the student app or dashboard — local demo only.
* Demo mode state (history, toggle) lives in the dashboard pod's memory; a dashboard restart resets it to the YAML defaults.
* The Student app's `Restore` / failure-injection endpoints (`/control/*`) are intentionally unauthenticated for the demo.

## 9. Files
```
app/        app.py (health endpoints, wiring) · students.py (CRUD + SQLite) · static/index.html (UI) · Dockerfile · requirements.txt
dashboard/  server.py (K8s API reader, actions, demo mode) · static/index.html · Dockerfile · requirements.txt
k8s/        pvc.yaml · deployment.yaml · service.yaml · dashboard.yaml · dashboard-rbac.yaml
scripts/    deploy.ps1 · status.ps1 · cleanup.ps1 · run-tests.ps1   (+ the original *.sh scripts, updated to :2.0)
tests/      test_*.py (offline) · seed_students.py · verify_persistence.py · verify_scenarios.py (cluster)
docs/       ARCHITECTURE.md · VERIFIED_RUN.md (run of the original, pre-upgrade project)
```
