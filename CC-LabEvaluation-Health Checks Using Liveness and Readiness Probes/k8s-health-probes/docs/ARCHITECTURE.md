# Architecture

```
 Your laptop                       Kubernetes cluster (Docker Desktop / minikube / kind)
 ┌──────────────┐  port-forward   ┌──────────────────────────────────────────────────────────┐
 │  Browser     │────────────────▶│ Service: health-dashboard (NodePort 30090)               │
 │ localhost:8080                 │   └─▶ Pod: health-dashboard  (Flask :8080)               │
 └──────────────┘                 │         │  1. reads pods/endpoints/events/deployment      │
                                  │         │     from the Kubernetes API (ServiceAccount)    │
                                  │         │  2. GET  <podIP>:5000/info   (app state)        │
                                  │         │  3. POST <podIP>:5000/control/...  (inject)     │
                                  │         │  4. PATCH deployment (slow start-up)            │
                                  │         ▼                                                  │
                                  │ Service: health-demo-svc (NodePort 30080 -> :5000)        │
                                  │   routes ONLY to Ready pods (the "endpoints" list)        │
                                  │   ├─▶ Pod health-demo-xxxx-1  ┐                            │
                                  │   ├─▶ Pod health-demo-xxxx-2  ├ Flask :5000 (/healthz,/ready)│
                                  │   └─▶ Pod health-demo-xxxx-3  ┘        ▲                   │
                                  │                                        │ kubelet probes    │
                                  │    kubelet ── GET /healthz (liveness)  │ every 5 s         │
                                  │            └─ GET /ready   (readiness) ┘                   │
                                  └──────────────────────────────────────────────────────────┘
```

## Who decides what

| Component | Decision | Triggered by |
|-----------|----------|--------------|
| **kubelet** (on the node) | restart the container | liveness probe fails 3 times in a row |
| **kubelet + endpoint controller** | remove the pod IP from the Service | readiness probe fails 3 times in a row |
| **Deployment / ReplicaSet** | keep 3 replicas, roll out new pods | pod template change (slow start-up patch) |
| **Dashboard** | *observe and inject only* - never decides health | reads K8s API, calls pod endpoints |

The dashboard never fakes anything: the numbers are the Kubernetes API's numbers.

## How each failure is produced (and why it is realistic)

* **Liveness failure** - `POST /control/liveness` flips an in-memory flag so `/healthz` returns **500**.
  The kubelet sees 3 consecutive failures (3 x 5 s) and kills the container. Because the flag is only in
  memory, the *new* container starts clean, which is exactly how a restart "heals" a hung process.
* **Readiness failure** - `POST /control/readiness` makes `/ready` return **503**. The container keeps
  running (no restart) but after 3 failures the pod is NotReady and Kubernetes drops its IP from the
  Service endpoints. `POST /control/reset` brings it back.
* **Slow start-up** - the dashboard patches the Deployment env var `STARTUP_DELAY_SECONDS=30`. Kubernetes
  performs a genuine rolling update; each new container answers `/ready` with 503 for its first 30 s
  (while `/healthz` stays 200 so liveness doesn't kill a booting app). The Deployment uses
  `maxSurge: 100%, maxUnavailable: 0`, so the old pods keep serving until the new ones are Ready.

## Where the dashboard's "probe status" comes from

The app records the **last request that carried the kubelet's User-Agent (`kube-probe/…`)** and its HTTP
status, and exposes it at `/info`. So "Liveness probe: Failing - last kubelet probe HTTP 500, 2 s ago" is
the real probe result, not a guess. Requests from the dashboard or curl are ignored for this purpose.

## Why the dashboard runs inside the cluster

Pod IPs are only reachable from inside the cluster network. Running the dashboard as a pod lets it call each
pod directly (so a failure can be injected on one *selected* pod, which a Service would not allow) and talk to
the Kubernetes API with a least-privilege Role (`k8s/dashboard-rbac.yaml`: read pods/endpoints/events,
patch the one Deployment).

## Student Management upgrade (added)

* **Application** - `app/app.py` (health endpoints) + `app/students.py` (CRUD blueprint, SQLite). Same Deployment
  `health-demo`, same Service `health-demo-svc`, now serving the UI at `/` and the API at `/api/students`.
* **Persistence** - `k8s/pvc.yaml` (`student-data`, 1 Gi, ReadWriteOnce) mounted at `/data`; the database is
  `/data/students.db`. All 3 pods open the same file; writes use `BEGIN IMMEDIATE` + a 5 s busy timeout.
* **Probes** - startup `/startupz` (2 s x 30), liveness `/healthz` (5 s x 3, never touches the DB), readiness
  `/ready` (5 s x 3, checks the DB). Timeouts are 2 s.
* **Automatic demo mode** - a thread in the dashboard calls `POST /control/liveness|readiness` with
  `duration_seconds` on ONE healthy pod every `DEMO_INTERVAL_SECONDS` (default 120), alternating kinds, only when all
  pods are healthy. The app auto-clears the failure at expiry; the dashboard records detection/recovery times from the
  Kubernetes API (restart count, Ready condition). No extra RBAC is needed.
