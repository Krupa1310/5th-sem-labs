# Health Checks Using Liveness and Readiness Probes

**Cloud Computing (26ECAC301) · Lab Evaluation – 2 · Problem 14 – Kubernetes & Microservices Deployment**
KLE Technological University · Department of CSE (Artificial Intelligence)

A working Kubernetes project that **demonstrates, with real pods, how Kubernetes restarts unhealthy
containers (liveness probe) and stops sending traffic to pods that are not ready (readiness probe)**,
plus a live monitoring dashboard.

> **Status of testing** – the three scenarios and every dashboard button were run against a real
> Kubernetes cluster (k3s v1.30.5) and passed 23/23 automated checks; the raw output is in
> [`docs/VERIFIED_RUN.md`](docs/VERIFIED_RUN.md). The sandbox I developed in had no Docker, so the
> `docker build` and "load image into minikube/kind" steps in `scripts/deploy.sh` are **written but not
> yet run by me** – run them once on your laptop before the evaluation (a 5-minute dry run), and see
> [Troubleshooting](#10-troubleshooting).

---

## Contents
1. [Introduction](#1-introduction) · 2. [Problem statement](#2-problem-statement) · 3. [Objectives](#3-objectives) · 4. [Architecture](#4-architecture) · 5. [Technologies](#5-technologies-used) · 6. [Installation & run](#6-installation--running-it) · 7. [Docker & Kubernetes commands explained](#7-docker-and-kubernetes-commands-explained) · 8. [Testing the 3 scenarios](#8-testing-procedures) · 9. [Expected observations](#9-expected-observations) · 10. [Troubleshooting](#10-troubleshooting) · 11. [Every file explained](#11-what-every-file-does)

## 1. Introduction
Kubernetes restarts crashed containers by itself, but by default it only knows whether a container's
*process* is running – not whether the *application* works. A web server can deadlock, take a minute to
load data at start-up, or lose its database while its process stays alive; Kubernetes would still send it
users. **Probes** close this gap: the **kubelet** (the agent on each node) periodically calls an endpoint
in your app and acts on the result.

| Probe | Question | If it fails |
|---|---|---|
| **Liveness** | Is the container still working? | Container is **killed and restarted** |
| **Readiness** | Can it serve traffic right now? | Pod is **removed from Service endpoints**, *no restart* |
| Startup | Has it finished starting? | Container restarted; other probes wait (discussed, not needed here) |

## 2. Problem statement
*Configure liveness and readiness probes for an application on Kubernetes and demonstrate how Kubernetes
restarts unhealthy containers and stops sending traffic to pods that are not ready.*
Show: HTTP probes in the pod spec · a simulated failure or slow start-up · the resulting pod status,
restart count and Service endpoints.

## 3. Objectives
* Add HTTP liveness (`/healthz`) and readiness (`/ready`) probes with the specified timings.
* Run **3 replicas** behind a Service so traffic can shift between healthy pods.
* **A.** Liveness failure → automatic container restart, restart count +1, recovery.
* **B.** Readiness failure → pod stays Running but `0/1`, **no** restart, IP leaves the endpoints, then returns.
* **C.** 30 s slow start-up → pod Running but NotReady, Service sends it nothing until ready.
* Provide a dashboard that shows **real** cluster data and has buttons to trigger/restore each scenario.

## 4. Architecture
Full diagram and explanation: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). In short:

```
Browser ─▶ health-dashboard pod ─▶ Kubernetes API   (pods, restarts, endpoints, events)
                              └─▶ each health-demo pod's IP  (/info, /control/*)
Users   ─▶ Service health-demo-svc ─▶ only READY pods of the Deployment (3 × Flask app)
kubelet ─▶ GET /healthz every 5 s (liveness)   GET /ready every 5 s (readiness)
```

## 5. Technologies used
Python 3.12 · Flask 3.0 · Docker · Kubernetes (Deployment, Service, ServiceAccount/Role/RoleBinding) ·
YAML · HTML/CSS/JavaScript (dashboard, no frameworks). No third-party Python packages besides Flask –
the dashboard talks to the Kubernetes REST API using only the standard library.

## 6. Installation & running it

### 6.1 What you need on your laptop
1. **Docker Desktop** (Windows/macOS) or Docker Engine (Linux).
2. **A local Kubernetes cluster**, any one of:
   * **Docker Desktop → Settings → Kubernetes → Enable** *(easiest; this is what I'd suggest)*
   * `minikube start` · or `kind create cluster`
3. `kubectl` (included with Docker Desktop).
4. Python 3 *(only for the optional `tests/verify_scenarios.py`)*.

Windows users: run the `.sh` scripts in **Git Bash** or **WSL**, or just copy the commands from §7.

### 6.2 Run it (3 commands)
```bash
cd k8s-health-probes
bash scripts/check-env.sh        # 1. is Docker + Kubernetes ready?
bash scripts/deploy.sh           # 2. build images, deploy 3 pods + Service + dashboard
bash scripts/open-dashboard.sh   # 3. then open http://localhost:8080  (leave this terminal open)
```
First deploy takes ~1–3 minutes (image build). To remove everything later: `bash scripts/cleanup.sh`.

## 7. Docker and Kubernetes commands explained
`deploy.sh` just runs these; you can type them yourself.

| Command | What it does (plain English) |
|---|---|
| `docker build -t health-demo:1.0 app` | Packages the Flask app (`app/`) into an *image* named `health-demo:1.0`. |
| `docker build -t health-dashboard:1.0 dashboard` | Same for the dashboard. |
| `minikube image load health-demo:1.0` / `kind load docker-image …` | minikube/kind run in their own container, so copy the image into them. *Docker Desktop shares images, no step needed.* |
| `kubectl apply -f k8s/deployment.yaml` | "Make the cluster look like this file": creates the 3-replica Deployment with both probes. |
| `kubectl apply -f k8s/service.yaml` | Creates the Service that load-balances to Ready pods. |
| `kubectl apply -f k8s/dashboard-rbac.yaml -f k8s/dashboard.yaml` | Deploys the dashboard and gives it *read* access to pods plus permission to patch one Deployment. |
| `kubectl get pods` | Lists pods: **READY** (`1/1` ready, `0/1` not), **STATUS**, **RESTARTS**. |
| `kubectl get pods -w` | Same, but live-updating (`-w` = watch). Ctrl+C to stop. |
| `kubectl get endpoints health-demo-svc` | The Service's list of pod IPs that receive traffic – **the key readiness evidence**. |
| `kubectl describe pod <name>` | Details + **Events** (`Liveness probe failed…`, `Killing…`). |
| `kubectl logs <name> --previous` | Logs of the container *before* its last restart. |
| `kubectl set env deployment/health-demo STARTUP_DELAY_SECONDS=30` | Changes the app's start-up delay → triggers a rolling update (Scenario C). |

## 8. Testing procedures

### 8.1 Using the dashboard (best for the demo)
Open **http://localhost:8080**. Everything refreshes every 2 s. Pick a **Target pod** in the dropdown.

**A – Liveness failure**
1. Click **Trigger Liveness Failure**. The pod's *Liveness probe* column turns **Failing** (HTTP 500).
2. After ~15 s (3 failed probes × 5 s) the **Restarts** cell goes **0 → 1**, events show
   `Unhealthy: Liveness probe failed…` and `Killing: … will be restarted`.
3. The pod returns to `1/1`, *Passing*, and the scenario banner clears (the new container starts clean).

**B – Readiness failure**
1. Click **Trigger Readiness Failure**. Readiness column turns **Failing** (HTTP 503).
2. After ~15 s the pod's READY goes **1/1 → 0/1**, STATUS stays **Running**, **Restarts unchanged**,
   *In Service?* → **No**, and its IP moves to **NotReady (excluded)** in *Service endpoints*.
3. Click **Send 30 requests through the Service** – the failing pod gets **0** requests.
4. Click **Restore** on that pod (or **Restore Application Health**) – READY returns to `1/1`
   and the IP is added back.

**C – Slow start-up**
1. Click **Simulate Slow Startup**. Kubernetes starts 3 new pods (a real rolling update).
2. For ~30 s the new pods are **Running but 0/1**, listed under *NotReady* endpoints; **Restarts 0**.
   Click *Send 30 requests* now: only the **old** pods answer, **0 failures**.
3. After ~30 s the new pods become `1/1` and join the endpoints, the old pods terminate.
4. Click **Restore Application Health** to set the delay back to 0 (another quick rolling update).

### 8.2 Using only kubectl (shows the raw commands)
```bash
bash scripts/demo-cli.sh status      # pods + endpoints
bash scripts/demo-cli.sh liveness    # inject, then watch RESTARTS rise
bash scripts/demo-cli.sh readiness   # inject, then watch READY 0/1
bash scripts/demo-cli.sh slowstart   # 30 s delay rollout
bash scripts/demo-cli.sh restore
```
Handy side-by-side terminals during the demo: `kubectl get pods -w` and
`watch kubectl get endpoints health-demo-svc` (macOS: `brew install watch`).

### 8.3 Automated verification (independent of the dashboard)
```bash
python tests/verify_scenarios.py              # all 3 scenarios, ~4 min, prints PASS/FAIL per check
python tests/verify_scenarios.py liveness     # or readiness | slowstart
```

## 9. Expected observations
| Stage | Pod READY | Restarts | Service endpoints |
|---|---|---|---|
| Healthy | `1/1` Running | 0 | all 3 pod IPs |
| Slow start-up | `0/1` Running | 0 | new pod only in *notReadyAddresses* until ready |
| Readiness failing | `0/1` Running | 0 (unchanged) | failing pod's IP removed |
| Liveness failing | restarts, then `1/1` Running | **+1** | still listed until the kill, then re-added |

Notes that often surprise people:
* **Timing is ~15 s, not instant.** `periodSeconds: 5` × `failureThreshold: 3`. (Readiness uses Kubernetes'
  default `failureThreshold: 3`.) During the first ~15 s of a *readiness* failure the pod still shows `1/1` –
  that is correct, not a bug.
* In the liveness scenario the pod **stays Ready until it is killed**, because readiness is still passing.
* The injected failure is stored in memory, so a **restart clears it** – this is why the pod "recovers".

Real captured output: [`docs/VERIFIED_RUN.md`](docs/VERIFIED_RUN.md).

## 10. Troubleshooting
| Symptom | Cause / fix |
|---|---|
| `check-env.sh`: Docker daemon not reachable | Start Docker Desktop and wait for the whale icon to settle. |
| `kubectl cluster-info` fails | Enable Kubernetes in Docker Desktop (wait for the green light), or `minikube start` / `kind create cluster`. Check `kubectl config current-context`. |
| Pods stuck in `ErrImagePull` / `ImagePullBackOff` / `ErrImageNeverPull` | The cluster can't see your local image. **minikube:** `minikube image load health-demo:1.0` (and `health-dashboard:1.0`). **kind:** `kind load docker-image health-demo:1.0 health-dashboard:1.0`. **Docker Desktop:** in recent versions with the *kind* provisioner, enable *Settings → General → "Use containerd for pulling and storing images"*, or use the *kubeadm* provisioner. Then `kubectl rollout restart deployment/health-demo deployment/health-dashboard`. |
| Dashboard page loads but says "Cannot load cluster data" | `kubectl logs deploy/health-dashboard`; check RBAC applied: `kubectl get role,rolebinding health-dashboard`. |
| `bash scripts/open-dashboard.sh`: "address already in use" | Something uses port 8080. Run `kubectl port-forward svc/health-dashboard 9090:80` and open `localhost:9090`. |
| Liveness probe column shows **Unreachable** for a pod | The app isn't answering yet (still starting) or the pod is being replaced; wait a few seconds. |
| Restart count never changes after "Trigger Liveness Failure" | Wait ~20 s (3 probes × 5 s plus the probe cycle). If still nothing: `kubectl describe pod <name>` and look at Events. |
| Pod IP still in endpoints right after Readiness failure | Expected for ~15 s (3 failed probes). |
| "Restore" seems to do a lot after Slow Startup | Correct – removing the delay is itself a rolling update (new pods, new names). |
| Port 30080 / 30090 not reachable on minikube | Use `minikube service health-demo-svc --url` or just use the port-forward script. |
| Windows: `bash: scripts/deploy.sh` problems | Use Git Bash/WSL; if you see `\r` errors run `dos2unix scripts/*.sh`. |
| Want to see the raw app logs | `kubectl logs <pod>`; every probe request appears (every 5 s) – injected failures print `LIVENESS FAILURE INJECTED`. |

## 11. What every file does
```
k8s-health-probes/
├── app/                          # ── the sample application ("Flask application" + its Dockerfile + requirements)
│   ├── app.py                    #   Flask app: /healthz (200/500), /ready (200/503), /whoami, /info,
│   │                             #   POST /control/liveness|readiness|reset, POST /crash; 30 s start-up delay
│   │                             #   via STARTUP_DELAY_SECONDS; records the kubelet's probe results.
│   ├── Dockerfile                #   Builds image health-demo:1.0 (python:3.12-slim, port 5000)
│   └── requirements.txt          #   Flask==3.0.3
├── dashboard/                    # ── monitoring dashboard ("Dashboard/frontend")
│   ├── server.py                 #   Backend: reads K8s API + pod /info, runs the button actions (RBAC-limited)
│   ├── static/index.html         #   Frontend: HTML+CSS+JS, polls /api/status every 2 s
│   ├── Dockerfile                #   Builds image health-dashboard:1.0
│   └── requirements.txt          #   Flask==3.0.3
├── k8s/                          # ── Kubernetes manifests (YAML)
│   ├── deployment.yaml           #   3 replicas, liveness+readiness probes exactly as specified, rolling-update settings
│   ├── service.yaml              #   health-demo-svc (NodePort 30080 → 5000); routes to Ready pods only
│   ├── dashboard-rbac.yaml       #   ServiceAccount + Role + RoleBinding for the dashboard (least privilege)
│   └── dashboard.yaml            #   Dashboard Deployment + Service (NodePort 30090)
├── scripts/
│   ├── check-env.sh              #   Verifies Docker, kubectl and cluster access
│   ├── deploy.sh                 #   Build → load into cluster → apply → wait
│   ├── open-dashboard.sh         #   kubectl port-forward → http://localhost:8080
│   ├── demo-cli.sh               #   Terminal-only version of the three demonstrations
│   └── cleanup.sh                #   Delete everything created
├── tests/
│   └── verify_scenarios.py       #   Automated end-to-end proof of all 3 scenarios using only kubectl
└── docs/
    ├── ARCHITECTURE.md           #   Diagram + who-decides-what + how failures are produced
    └── VERIFIED_RUN.md           #   Real captured output from the test run
```
**Key design choices worth mentioning to the evaluator**
* Probes in `k8s/deployment.yaml` match the brief exactly (liveness: `/healthz`, delay 5, period 5, threshold 3;
  readiness: `/ready`, delay 3, period 5).
* `/healthz` returns 200 during slow start-up, so liveness doesn't kill a booting app (the DOCX notes a startup
  probe as the alternative for very slow boots).
* Liveness only checks the app itself, not external dependencies (best practice from the slides).
* `maxSurge: 100%, maxUnavailable: 0` keeps old pods serving during the slow-start rollout.
