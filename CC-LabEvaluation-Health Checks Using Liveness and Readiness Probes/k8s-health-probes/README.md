# ☸️ KUBERNETES HEALTH CHECKS USING LIVENESS AND READINESS PROBES

## 🧪 CLOUD COMPUTING — LAB EVALUATION

**Student Management Application with Startup, Liveness and Readiness Probes**

**Course:** Cloud Computing (26ECAC301) · **Lab Evaluation – 2** · **Problem 14**  
**Institution:** KLE Technological University

A Student Management web application deployed on Kubernetes using three application pods. Kubernetes startup, liveness and readiness probes monitor the application, while a Persistent Volume Claim stores student records. A live monitoring dashboard displays pod health, probe status, service endpoints, restart counts and failure/recovery events.

| Component | Local URL |
|---|---|
| Student Management Application | `http://localhost:30080` |
| Kubernetes Monitoring Dashboard | `http://localhost:30090` |


## 0️⃣ Verification Scope — What Was Tested and What Was Not

The project documentation distinguishes offline and simulated checks from tests that require a real Docker Desktop Kubernetes cluster. This is important when presenting the project during evaluation.

| Verified in the development environment | Requires a run on your laptop / real cluster |
|---|---|
| 44 offline unit tests covering student CRUD, search, validation, duplicate handling, health endpoints, probe behaviour, dashboard logic and manifest consistency | Building the two Docker images |
| Three separate application processes sharing one SQLite database; 300 concurrent writes completed without database-lock errors, and data remained intact after a process restart | Applying the Kubernetes manifests, binding the PVC on Docker Desktop and running three pods against the shared volume |
| Student web UI tested in headless Chromium: add, edit, delete, search, inline validation, duplicate detection, persistence after reload and mobile layout | Real kubelet checks against `/startupz` and the database-aware `/ready` endpoint |
| Dashboard UI tested in Chromium against a simulated cluster, including pods, endpoints, probes and demo history | Automatic demo mode against real pods; its logic was unit-tested against a simulated cluster |
| YAML parsing and consistency checks for image tags, probe paths, PVC mount, selectors and RBAC | PowerShell scripts and cluster verification scripts (`verify_persistence.py` and `verify_scenarios.py`) against the upgraded Deployment |

**Important:** The development verification notes were produced in an environment without Docker, Kubernetes or PowerShell. Run the deployment and cluster tests on your own laptop before the lab evaluation. The original project dashboard and three probe scenarios were previously verified on a real k3s cluster; see `docs/VERIFIED_RUN.md`. That historical run predates the Student Management upgrade and is not evidence that the upgraded deployment has already been tested on your current cluster.

---

## 📑 Table of Contents

1. [Verification Scope](#0️⃣-verification-scope--what-was-tested-and-what-was-not)
2. [Aim](#-aim)
3. [Problem Statement](#-problem-statement)
4. [Objectives](#-objectives)
5. [What Changed and What Was Kept](#-what-changed-and-what-was-kept)
6. [Technologies and Configuration](#️-technologies-and-configuration)
7. [Architecture](#️-architecture)
8. [Project Structure](#-project-structure)
9. [Checkpoint 1 – Student Management Application](#1️⃣-checkpoint-1--student-management-application)
10. [Checkpoint 2 – Docker Containerization](#2️⃣-checkpoint-2--docker-containerization)
11. [Checkpoint 3 – Kubernetes Deployment](#3️⃣-checkpoint-3--kubernetes-deployment)
12. [Checkpoint 4 – Startup, Liveness and Readiness Probes](#4️⃣-checkpoint-4--startup-liveness-and-readiness-probes)
13. [Checkpoint 5 – Monitoring Dashboard and Failure Demonstration](#5️⃣-checkpoint-5--monitoring-dashboard-and-failure-demonstration)
14. [Execution](#️-execution)
15. [Probe Configuration](#-probe-configuration)
16. [Testing and Verification](#-testing-and-verification)
17. [Demonstration Procedure](#-demonstration-procedure)
18. [Results and Analysis](#-results-and-analysis)
19. [Student Management API](#-student-management-api)
20. [Troubleshooting](#️-troubleshooting)
21. [Design Points for Evaluation](#-design-points-for-evaluation)
22. [Best Practices](#-best-practices)
23. [Automatic Demo Mode Safety](#️-automatic-demo-mode-safety)
24. [Known Limitations](#️-known-limitations)
25. [Files and Responsibilities](#-files-and-responsibilities)
26. [Conclusion](#-conclusion)
27. [Authors](#-authors)

## 🎯 Aim

To deploy a Student Management application on Kubernetes and implement startup, liveness and readiness probes to monitor application health. The experiment demonstrates how Kubernetes detects startup delays and application failures, restarts unhealthy containers, removes unready pods from Service endpoints, and maintains application availability using multiple replicas. Persistent storage and a monitoring dashboard are also used to demonstrate data retention and cluster health.

## 📌 Problem Statement

Applications deployed in containers may take time to start, become temporarily unable to serve requests, or stop functioning correctly. Kubernetes must distinguish between an application that is still starting, an application that needs to be restarted, and an application that is running but cannot currently handle user requests.

In this experiment, a Student Management web application is deployed on Kubernetes with three replicas. The application uses:

- **Startup Probe** to check whether application initialization and database setup have completed.
- **Liveness Probe** to determine whether the application process is healthy. If it repeatedly fails, Kubernetes restarts the container.
- **Readiness Probe** to determine whether a pod can serve requests. If it fails, Kubernetes removes that pod from the Service's ready endpoints without restarting it.

A monitoring dashboard displays the actual Kubernetes pod state and provides controlled demonstrations of liveness failure, readiness failure and slow startup.

## 🎯 Objectives

The main objectives of this experiment are:

- To develop a Student Management web application using Python and Flask.
- To containerize the application and monitoring dashboard using Docker.
- To deploy the application on Kubernetes with three replicas.
- To configure startup, liveness and readiness probes.
- To understand the difference between container restart and pod readiness status.
- To demonstrate automatic container recovery after liveness probe failure.
- To demonstrate removal of an unready pod from Service endpoints.
- To simulate slow application startup using a rolling update.
- To store student records using a Persistent Volume Claim.
- To monitor pods, probes, endpoints, events and restart counts through a dashboard.

## 🔄 What Changed and What Was Kept

The Student Management upgrade extends the original Kubernetes health-check demonstration while preserving its main deployment and dashboard workflow.

**Kept from the original project:**
- Application Deployment name `health-demo` with 3 replicas.
- Application Service `health-demo-svc` on NodePort `30080`.
- Dashboard Deployment and Service on NodePort `30090`.
- Dashboard RBAC configuration in `k8s/dashboard-rbac.yaml`.
- Existing probe and control endpoints, including `/healthz`, `/ready`, `/whoami`, `/info`, `/control/*` and `/crash`.
- Dashboard controls, rolling-update settings, `demo-cli.sh` and `verify_scenarios.py`.

**Added or updated:**

| Area | Change |
|---|---|
| `app/students.py` | Student CRUD REST API, SQLite storage and validation |
| `app/static/index.html` | Responsive Student Management interface |
| `app/app.py` | Student API integration, `/startupz`, database-aware `/ready`, and automatically expiring injected failures |
| `k8s/pvc.yaml` | New 1 GiB `student-data` volume for the SQLite database |
| `k8s/deployment.yaml` | Application image `health-demo:2.0`, `/data` volume mount, startup probe and explicit probe settings |
| `dashboard/server.py` and dashboard UI | Student count, database status, startup probe details, automatic demo mode and failure/recovery history |
| `k8s/dashboard.yaml` | Dashboard image `health-dashboard:2.0` and demo-mode settings |
| `scripts/*.ps1` | PowerShell deployment, status, cleanup and test scripts |
| `tests/` | Offline unit tests, sample-data seeding and cluster persistence/scenario checks |

The image tags were changed from `:1.0` to `:2.0` so Kubernetes creates updated pods when the pod specification changes. Rebuilding an image with the same tag may otherwise leave existing pods running the older image.

## 🛠️ Technologies and Configuration

| Component | Technology / Configuration |
|---|---|
| Application | Student Management System |
| Programming Language | Python |
| Web Framework | Flask |
| Frontend | HTML, CSS and JavaScript |
| Database | SQLite |
| Containerization | Docker |
| Orchestration | Kubernetes |
| Deployment | Kubernetes Deployment and Service |
| Persistent Storage | PersistentVolumeClaim (PVC), 1 GiB |
| Application Replicas | 3 pods |
| Application Container Port | 5000 |
| Application NodePort | 30080 |
| Dashboard Container Port | 8080 |
| Dashboard NodePort | 30090 |
| Application Image | `health-demo:2.0` |
| Dashboard Image | `health-dashboard:2.0` |
| Health Endpoints | `/startupz`, `/healthz`, `/ready` |

## 🏗️ Architecture

The project contains a Student Management application and a monitoring dashboard deployed inside a Kubernetes cluster.

```text
                         USER / BROWSER
                               |
                +--------------+--------------+
                |                             |
                v                             v
       Student Application             Monitoring Dashboard
       http://localhost:30080          http://localhost:30090
                |                             |
                v                             v
       +-------------------+         +----------------------+
       | Service           |         | Dashboard Service    |
       | health-demo-svc   |         | health-dashboard     |
       | NodePort: 30080   |         | NodePort: 30090       |
       +-------------------+         +----------------------+
                |                             |
        Ready pods only                       v
                |                    Dashboard Deployment
       +--------+--------+            (1 dashboard pod)
       |        |        |                     |
       v        v        v                     v
    +------+ +------+ +------+         Kubernetes API
    | Pod 1| | Pod 2| | Pod 3|         Pods / Events /
    | Flask| | Flask| | Flask|         Endpoints / Deployment
    | :5000| | :5000| | :5000|
    +------+ +------+ +------+
       |        |        |
       +--------+--------+
                |
                v
       Persistent Volume Claim
          student-data (1 GiB)
                |
                v
        SQLite: /data/students.db

       Kubelet performs probes on each application pod:
       /startupz  -> Startup Probe
       /healthz   -> Liveness Probe
       /ready     -> Readiness Probe
```

### Component Responsibilities

**1. Student Management Application**

- Provides the web interface for adding, viewing, editing, deleting and searching student records.
- Exposes REST API endpoints for student operations.
- Provides health endpoints used by Kubernetes probes.
- Stores records in SQLite at `/data/students.db` on the persistent volume.

**2. Kubernetes Deployment — `health-demo`**

- Maintains three application replicas.
- Applies startup, liveness and readiness probes to each application container.
- Replaces containers that fail liveness checks.
- Uses rolling-update settings so existing ready pods can continue serving traffic during the slow-start demonstration.

**3. Service — `health-demo-svc`**

- Exposes the Student Management application through NodePort `30080`.
- Routes requests only to pods that are Ready.
- Excludes pods that fail readiness checks from its ready endpoints.

**4. Monitoring Dashboard**

- Reads pod, endpoint, deployment and event information from the Kubernetes API.
- Displays probe configuration and status, pod readiness, restart counts and student database status.
- Provides controls to inject liveness and readiness failures, simulate slow startup and restore application health.
- Supports automatic demonstration mode with short-lived failures.

**5. Persistent Volume Claim**

- Provides a 1 GiB persistent volume named `student-data`.
- Mounts the volume at `/data` inside application pods.
- Keeps student records outside the container filesystem so they survive container and pod restarts.

## 📁 Project Structure

```text
k8s-health-probes/
│
├── app/
│   ├── app.py                    # Flask app and health/probe endpoints
│   ├── students.py               # Student CRUD API and SQLite operations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── static/
│       └── index.html            # Student Management web interface
│
├── dashboard/
│   ├── server.py                 # Kubernetes monitoring and demo logic
│   ├── requirements.txt
│   ├── Dockerfile
│   └── static/
│       └── index.html            # Monitoring dashboard interface
│
├── k8s/
│   ├── deployment.yaml           # 3-replica application Deployment and probes
│   ├── service.yaml               # Student application NodePort Service
│   ├── pvc.yaml                   # Persistent Volume Claim
│   ├── dashboard.yaml             # Dashboard Deployment and Service
│   └── dashboard-rbac.yaml        # Dashboard ServiceAccount and permissions
│
├── scripts/
│   ├── deploy.ps1                # Build and deploy on Docker Desktop (PowerShell)
│   ├── status.ps1                # Cluster status
│   ├── cleanup.ps1               # Cleanup options
│   ├── run-tests.ps1             # Run offline tests
│   ├── deploy.sh                 # Build and deploy (Bash)
│   ├── cleanup.sh
│   ├── open-dashboard.sh
│   ├── demo-cli.sh               # Terminal-based probe demonstrations
│   └── check-env.sh
│
├── tests/
│   ├── test_students_api.py
│   ├── test_health_endpoints.py
│   ├── test_dashboard_demo.py
│   ├── test_manifests.py
│   ├── verify_persistence.py     # Cluster persistence test
│   ├── verify_scenarios.py       # Cluster probe scenarios
│   └── seed_students.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── VERIFIED_RUN.md
│
└── README.md
```

## 1️⃣ Checkpoint 1 – Student Management Application

A web application was developed using Python and Flask.

The application supports the following operations:

- Add a student record.
- View all student records.
- Search student records.
- Update an existing student record.
- Delete a student record.
- Validate student details and prevent duplicate student IDs or email addresses.

Student data is stored in an SQLite database. The database file is configured at `/data/students.db` when the application runs in Kubernetes.

## 2️⃣ Checkpoint 2 – Docker Containerization

Separate Docker images are built for the Student Management application and the monitoring dashboard.

| Component | Docker Image | Container Port |
|---|---|---:|
| Student Management Application | `health-demo:2.0` | 5000 |
| Monitoring Dashboard | `health-dashboard:2.0` | 8080 |

The Dockerfiles install the required Python dependencies and start the corresponding Flask application. The deployment scripts build both images before applying the Kubernetes manifests.

## 3️⃣ Checkpoint 3 – Kubernetes Deployment

The Student Management application is deployed using a Kubernetes Deployment named `health-demo` with **3 replicas**.

The application Service is named `health-demo-svc` and exposes the application through NodePort `30080`. The dashboard is deployed separately using `health-dashboard` and exposed through NodePort `30090`.

The PersistentVolumeClaim named `student-data` requests **1 GiB** of storage and is mounted at `/data` in each application pod.

Useful Kubernetes resources:

```powershell
kubectl get deployments
kubectl get pods -o wide
kubectl get services
kubectl get pvc
kubectl get endpoints health-demo-svc
```

## 4️⃣ Checkpoint 4 – Startup, Liveness and Readiness Probes

Three types of probes are configured in `k8s/deployment.yaml`.

### A. Startup Probe

- Endpoint: `GET /startupz`
- Checks whether application startup and database initialization have completed.
- Liveness and readiness checks are held until the startup probe succeeds.
- Allows the application time to initialize before Kubernetes evaluates the other probes.

### B. Liveness Probe

- Endpoint: `GET /healthz`
- Checks whether the application process is functioning.
- If the probe fails three consecutive times, Kubernetes restarts the container.
- The liveness endpoint does not depend on the database check.

### C. Readiness Probe

- Endpoint: `GET /ready`
- Checks whether the application can currently serve requests.
- It checks startup completion, injected readiness failure and database availability.
- If it fails three consecutive times, the pod becomes NotReady and is removed from the Service's ready endpoints.
- The container is **not restarted** just because readiness fails.

### Difference Between Liveness and Readiness

| Liveness Probe | Readiness Probe |
|---|---|
| Checks whether the container should continue running | Checks whether the pod can receive traffic |
| Failure causes the container to restart after the configured threshold | Failure marks the pod NotReady |
| Pod may continue to be part of the Deployment | Pod is removed from the Service's ready endpoints |
| Used to recover from an unhealthy application process | Used to stop sending requests to a temporarily unavailable pod |

### Probe Mechanisms

Kubernetes supports four probe mechanisms. This project uses `httpGet` because the Student Management application exposes HTTP health endpoints.

| Mechanism | How Kubernetes checks the container |
|---|---|
| `httpGet` | Sends an HTTP request. Status codes from 200 through 399 indicate success. |
| `tcpSocket` | Checks whether a TCP connection can be opened on the specified port. |
| `exec` | Runs a command inside the container; exit code `0` indicates success. |
| `grpc` | Calls a gRPC health-check endpoint and checks for the `SERVING` status. |

### Probe Timing Parameters

These fields control when probes run and how Kubernetes interprets their results. The values below are Kubernetes defaults; the project overrides the period, timeout and failure threshold as shown in the [Probe Configuration](#-probe-configuration) table.

| Field | Meaning | Kubernetes default |
|---|---|---:|
| `initialDelaySeconds` | Time to wait before the first probe starts | `0` seconds |
| `periodSeconds` | Time between consecutive probes | `10` seconds |
| `timeoutSeconds` | Maximum time to wait for a probe response | `1` second |
| `failureThreshold` | Consecutive failures before Kubernetes takes action | `3` |
| `successThreshold` | Consecutive successes required to mark the probe successful again | `1` |

With the project's five-second period and failure threshold of three, liveness or readiness failure is generally detected after about 15 seconds. Actual timing can vary slightly because probes run on intervals and include request timeouts.

## 5️⃣ Checkpoint 5 – Monitoring Dashboard and Failure Demonstration

The monitoring dashboard displays information from the Kubernetes cluster, including:

- Total application pods and healthy pods.
- Ready and NotReady pod counts.
- Container restart counts.
- Startup, liveness and readiness probe states.
- Service endpoints and NotReady endpoints.
- Student record count and database status.
- Failure detection and recovery history.

The dashboard supports the following demonstrations:

**1. Liveness Failure**

The dashboard or control endpoint injects a liveness failure. The `/healthz` endpoint returns HTTP 500. After three consecutive failed liveness checks (approximately 15 seconds with the configured period), Kubernetes restarts the container. The restart count increases, and the pod becomes Ready again after recovery.

**2. Readiness Failure**

The `/ready` endpoint returns HTTP 503. After three consecutive failed readiness checks, the pod changes from `1/1` to `0/1` while remaining Running. Its IP is removed from the Service's ready endpoints. The restart count does not increase. Once the failure is cleared, the pod becomes Ready and rejoins the endpoints.

**3. Slow Startup**

The Deployment is updated with `STARTUP_DELAY_SECONDS=30`. New pods remain NotReady while starting. The startup probe allows initialization time, and the liveness probe does not restart the application merely because it is still starting. Existing ready pods continue serving traffic until the new pods become Ready.

**4. Database Unavailable (Readiness Behaviour)**

If an application pod cannot access `/data/students.db`, its `/ready` endpoint returns HTTP 503 because the database is required to serve student requests. The pod becomes NotReady and is removed from the Service's ready endpoints, but `/healthz` can continue returning HTTP 200. Therefore, Kubernetes does not restart the container just because the database is unavailable. When database access is restored, successful readiness checks allow the pod to rejoin the Service. This describes the expected dependency-check behaviour; it is not a separate automatic demo-mode failure.

**5. Automatic Demonstration Mode**

The dashboard can automatically inject short-lived liveness and readiness failures, one at a time. It records detection and recovery information so the evaluator can observe the behaviour without manually triggering every scenario.

## ⚙️ Execution

### Prerequisites

- Docker Desktop installed and running.
- Kubernetes enabled in Docker Desktop.
- `kubectl` configured to use the `docker-desktop` context.
- Python 3.10 or later for running the test suite and helper scripts.

### Step 1 – Navigate to the Project Directory

```powershell
cd k8s-health-probes
```

### Step 2 – Verify the Environment

```powershell
docker --version
kubectl config current-context
kubectl get nodes
```

For the PowerShell deployment script, the current context should be `docker-desktop` and the node should be Ready.

### Step 3 – Build Docker Images and Deploy to Kubernetes

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1
```

The script builds both images, applies the PVC, deploys the application and dashboard, and waits for both Deployments to become available. It does not delete the existing persistent volume. The dashboard is updated in place, using the same Deployment, Service and RBAC resources.

### Equivalent Manual Deployment Commands

```powershell
docker build -t health-demo:2.0 app
docker build -t health-dashboard:2.0 dashboard
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl rollout status deployment/health-demo
kubectl apply -f k8s/dashboard-rbac.yaml -f k8s/dashboard.yaml
kubectl rollout status deployment/health-dashboard
```

### Step 4 – Verify the Deployment

```powershell
kubectl get pods -o wide
kubectl get deployments
kubectl get pvc student-data
kubectl get services
kubectl get endpoints health-demo-svc
```

Expected resources after a successful deployment:

- Three application pods managed by `health-demo`.
- One monitoring dashboard pod managed by `health-dashboard`.
- PVC `student-data` in `Bound` state.
- Application Service `health-demo-svc` on NodePort `30080`.
- Dashboard Service `health-dashboard` on NodePort `30090`.

### Step 5 – Open the Applications

- Student Management: `http://localhost:30080`
- Monitoring Dashboard: `http://localhost:30090`

If NodePort access is unavailable, use port forwarding in separate terminals:

```powershell
kubectl port-forward svc/health-demo-svc 30080:80
kubectl port-forward svc/health-dashboard 30090:80
```

### Step 6 – Add Sample Student Records (Optional)

```powershell
python .\tests\seed_students.py
```

## 📋 Probe Configuration

The following values are taken from `k8s/deployment.yaml` for the application container.

| Probe | HTTP Path | Port | Period | Timeout | Failure Threshold |
|---|---|---:|---:|---:|---:|
| Startup | `/startupz` | 5000 | 2 seconds | 2 seconds | 30 |
| Liveness | `/healthz` | 5000 | 5 seconds | 2 seconds | 3 |
| Readiness | `/ready` | 5000 | 5 seconds | 2 seconds | 3 |

**Important:** The liveness and readiness probes begin after the startup probe succeeds. The configured liveness and readiness failure thresholds are three consecutive failures.

## 🧪 Testing and Verification

### 1. Offline Unit Tests

These tests do not require a running Kubernetes cluster.

```powershell
pip install -r tests\requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1
```

Alternatively:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

| Test File | Verification |
|---|---|
| `test_students_api.py` | Student CRUD operations, search, validation, duplicate checks and database error handling |
| `test_health_endpoints.py` | Startup, liveness and readiness endpoints, injected failures and automatic expiry |
| `test_dashboard_demo.py` | Dashboard aggregation and automatic demonstration logic using a simulated cluster |
| `test_manifests.py` | Kubernetes manifest consistency, image names, probe paths, PVC mount, selectors and RBAC |

The project README records **44 offline tests passing** in its development verification. Run the commands above on your machine to verify the current checkout.

### 2. Kubernetes Cluster Tests

After deployment, pause automatic demo mode before running the cluster tests so that an automatically injected failure does not interfere with the results.

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:30090/api/demo" -ContentType "application/json" -Body '{"enabled":false}'
python .\tests\verify_persistence.py
python .\tests\verify_scenarios.py
```

The persistence test checks whether student data survives pod deletion and restart. The scenario test checks the liveness, readiness and slow-start behaviours against the cluster.

Re-enable automatic demo mode using the dashboard checkbox, or run:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:30090/api/demo" -ContentType "application/json" -Body '{"enabled":true}'
```

**Verification note:** `docs/VERIFIED_RUN.md` contains a real-cluster run of the earlier version of the probe demonstration (before the Student Management and startup-probe upgrade). Its 23/23 scenario checks are historical evidence for that earlier version; they should not be presented as a live test of the current upgraded deployment. The current upgrade's README records offline test coverage separately.

## 🖥️ Demonstration Procedure

Open the Student Management application and monitoring dashboard. In another PowerShell terminal, watch the application pods:

```powershell
kubectl get pods -l app=health-demo -w
```

### Part 1 – Student Management

1. Open `http://localhost:30080`.
2. Add a student record.
3. Edit and search for a record.
4. Delete a record.
5. Observe the pod information shown by the application and the student count on the dashboard.

### Part 2 – Liveness Failure

1. Open the monitoring dashboard.
2. Select **Trigger Liveness Failure** or use the terminal demo command.
3. Observe the liveness probe failure.
4. Wait for Kubernetes to restart the container.
5. Verify that the restart count increases and the pod returns to Ready state.

Terminal alternative:

```bash
./scripts/demo-cli.sh liveness
```

### Part 3 – Readiness Failure

1. Trigger a readiness failure from the dashboard.
2. Observe the pod change from `1/1` to `0/1` while its status remains Running.
3. Verify that the pod IP is removed from the ready Service endpoints.
4. Confirm that the restart count does not increase.
5. Restore the pod and verify that it returns to the endpoints.

Terminal alternative:

```bash
./scripts/demo-cli.sh readiness
```

### Part 4 – Slow Startup

1. Select **Simulate Slow Startup** on the dashboard.
2. Observe new pods in Running but NotReady state while startup is in progress.
3. Verify that the existing ready pods continue serving traffic.
4. Wait until the new pods become Ready.

Terminal alternative:

```bash
./scripts/demo-cli.sh slowstart
```

### Part 5 – Persistent Data Verification

Add a sample student record, then delete the application pods:

```powershell
kubectl delete pods -l app=health-demo
kubectl get pods -l app=health-demo -w
```

After the replacement pods become Ready, search for the same student record in the application. The record should remain available because the database is stored on the persistent volume.

### Restore the Application

```bash
./scripts/demo-cli.sh restore
```

### Automatic Demonstration Mode — Detailed Sequence

Automatic demonstration mode injects one short-lived failure at a time. In the documented default schedule, the first liveness failure begins about 30 seconds after the dashboard starts; a readiness failure follows later (approximately 2 minutes after the dashboard starts). The dashboard's **Inject now** control can be used to avoid waiting for the schedule.

- **Liveness:** `/healthz` returns HTTP 500. After three failed checks, Kubernetes kills and restarts the container. The restart count increases, and the pod returns to Ready after recovery.
- **Readiness:** `/ready` returns HTTP 503. The pod becomes `0/1` while remaining Running; it is removed from the Service's ready endpoints, and its restart count remains unchanged. When the injected failure expires, the pod rejoins the endpoints.
- **During both scenarios:** the other Ready replicas continue serving requests, so the Student Management application should remain available.

To demonstrate persistent data with a known record, create a record and then delete all application pods:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:30080/api/students" -ContentType "application/json" `
  -Body '{"student_id":"DEMO001","name":"Demo Student","email":"demo@example.com","department":"CSE","semester":4}'
kubectl delete pods -l app=health-demo
kubectl get pods -l app=health-demo -w
(Invoke-RestMethod "http://localhost:30080/api/students?q=DEMO001").students
```

After the replacement pods become Ready, the `DEMO001` record should still be present because the database is stored on the PVC.

## 📊 Results and Analysis

The expected behaviour of each probe scenario is summarized below. These are the designed Kubernetes outcomes; actual pod names, timestamps and restart counts depend on the cluster run.

| Scenario | Endpoint Result | Kubernetes Behaviour | Expected Observation |
|---|---|---|---|
| Normal operation | `/startupz`, `/healthz`, `/ready` return HTTP 200 when their conditions are satisfied | Pod remains Ready | `1/1 Running` and pod IP appears in ready endpoints |
| Startup in progress | `/startupz` returns HTTP 503 until initialization completes; `/ready` is also unavailable during startup delay | Startup probe gates the other probes; pod is not Ready | New pod remains NotReady while starting |
| Liveness failure | `/healthz` returns HTTP 500 | Kubelet restarts the container after 3 consecutive failures | Restart count increases; pod recovers after restart |
| Readiness failure | `/ready` returns HTTP 503 | Pod becomes NotReady and is removed from ready Service endpoints | Pod remains Running; restart count does not increase |
| Database unavailable | `/ready` returns HTTP 503 while `/healthz` can still return HTTP 200 | Pod is removed from ready Service endpoints; liveness does not trigger a restart | Pod remains Running and rejoins when database access returns |
| Recovery | Failure is cleared or expires | Successful readiness checks restore pod to Service endpoints | Pod returns to `1/1 Ready` |
| Pod restart / recreation | Application starts and database is initialized again | Deployment maintains the requested replica count | Student data remains available on the PVC |

### Overall Analysis

- Startup probes prevent liveness checks from restarting an application while it is still initializing.
- Liveness probes allow Kubernetes to recover from an application process that is no longer healthy.
- Readiness probes prevent traffic from being sent to a pod that cannot currently serve requests.
- A readiness failure does not itself restart the container.
- Multiple replicas allow the Service to continue routing traffic to other Ready pods when one pod becomes NotReady.
- Persistent storage keeps student records separate from the lifecycle of individual containers and pods.
- The monitoring dashboard makes the probe and recovery behaviour visible during the demonstration.

## 🔌 Student Management API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Student Management web interface |
| `GET` | `/api/students?q=text` | List and search student records |
| `POST` | `/api/students` | Add a student |
| `GET` | `/api/students/<id>` | Retrieve one student by database ID |
| `PUT` | `/api/students/<id>` | Update a student record |
| `DELETE` | `/api/students/<id>` | Delete a student record |
| `GET` | `/startupz` | Startup probe endpoint |
| `GET` | `/healthz` | Liveness probe endpoint |
| `GET` | `/ready` | Readiness probe endpoint |
| `GET` | `/whoami` | Return the serving pod name and IP |
| `GET` | `/info` | Return application, database and probe information |

The `POST /api/students` request accepts `student_id`, `name`, `email`, `department` and `semester` (1–8). Update requests can provide any subset of these fields. The API returns JSON errors for invalid input (400), missing records (404), duplicate student ID/email (409) and unavailable database (503).

Control endpoints used for demonstrations:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/control/liveness` | Inject or clear a liveness failure |
| `POST` | `/control/readiness` | Inject or clear a readiness failure |
| `POST` | `/control/reset` | Clear injected failures |
| `POST` | `/crash` | Liveness-failure demonstration alias |

## 🛠️ Troubleshooting

| Problem | Suggested Check / Solution |
|---|---|
| Wrong Kubernetes context | Run `kubectl config use-context docker-desktop` |
| Pods show `ErrImagePull` | Ensure the local Docker images are available to the Kubernetes cluster; check the deployment script and image names |
| PVC remains Pending | Run `kubectl describe pvc student-data` and `kubectl get storageclass`; confirm a default StorageClass exists |
| Pod remains `0/1` | Run `kubectl describe pod <pod-name>` and `kubectl logs <pod-name>`; inspect the readiness response and database status |
| Application URL is unavailable | Check the Service and pod status, or use the port-forward commands in the Execution section |
| Dashboard cannot load cluster data | Check `kubectl logs deployment/health-dashboard` and the dashboard RBAC resources |
| Automatic demo does not run | Check the dashboard demo-mode setting and whether all application pods are healthy |
| Need to stop automatic failures | Disable automatic demo mode in the dashboard or set `DEMO_MODE` to `off` in `k8s/dashboard.yaml` and re-apply it |

**Data warning:** The cleanup script keeps the persistent volume by default. Use the purge option only when you intentionally want to delete the stored student database.

## 🧠 Design Points for Evaluation

These are useful points to explain while demonstrating the project:

1. **Health endpoints are separate from business endpoints.** Kubernetes checks `/startupz`, `/healthz` and `/ready`; student CRUD operations use `/api/students`. A business-operation error does not automatically mean that the application process itself is unhealthy.
2. **Liveness does not check the database, but readiness does.** If the database is temporarily unavailable, restarting every application container would not solve the database problem. Readiness instead removes the affected pod from traffic until it can serve requests again.
3. **Startup probe protects slow initialization.** It gives the application up to 60 seconds (2-second period × 30 failures) to pass startup checks before liveness and readiness checks take over.
4. **The dashboard observes cluster state.** Pod status, restart counts, endpoints and events are read from the Kubernetes API. The dashboard is a monitoring and demonstration interface; Kubernetes and the kubelet make the probe and restart decisions.
5. **Persistent storage is separate from pod lifecycle.** Student records are stored on the PVC, not only in the container filesystem, so they can survive container restarts and pod replacement.

## 💡 Best Practices

- Keep health-check endpoints lightweight so they return quickly and do not add unnecessary load.
- Avoid checking the database or another external dependency in the liveness endpoint. Restarting every application pod during a database outage does not repair the database and can make recovery harder.
- Use readiness checks for dependencies that the application needs in order to serve requests. This project checks database availability through `/ready`.
- Choose probe periods, timeouts and thresholds based on measured startup and response times. Values that are too aggressive can cause unnecessary restarts; values that are too relaxed can delay failure detection.
- Use a startup probe when an application needs extra time to initialize, and keep important application data on persistent storage rather than in the container filesystem.

## 🛡️ Automatic Demo Mode Safety

- Only one injected failure is active at a time.
- A failure is injected only when the application pods are healthy, no other failure is active and no rollout is in progress.
- Injected readiness and liveness failures expire in the application itself (documented durations: 40 seconds for readiness and 75 seconds for liveness). This prevents a dashboard interruption from leaving a failure active indefinitely.
- Automatic demo mode does not modify or delete the student database.
- The default interval is 120 seconds and the minimum supported interval is 45 seconds.
- Demo mode is enabled by default in `k8s/dashboard.yaml` (`DEMO_MODE: "on"`). It can be paused using the dashboard checkbox or by setting it to `"off"` in the manifest and applying the dashboard configuration again.

## ⚠️ Known Limitations

- SQLite on a `ReadWriteOnce` volume is intended for a single-node local Kubernetes cluster such as Docker Desktop. The three pods share the volume on the same node. For a multi-node cluster, use a suitable database service such as MySQL/PostgreSQL or a `ReadWriteMany` storage solution.
- The Flask built-in development server is suitable for this lab demonstration; a production deployment should use a production WSGI server such as Gunicorn.
- The Student Management application and dashboard do not include authentication; they are intended for a local lab demonstration.
- Automatic demo history and toggle state are held in dashboard memory, so restarting the dashboard resets that state to the values in the YAML configuration.
- The demo control endpoints (`/control/*`) are intentionally unauthenticated for the lab demonstration. Do not expose this configuration as a production service.

## 📂 Files and Responsibilities

| Folder / File | Purpose |
|---|---|
| `app/` | `app.py` contains Flask wiring and health endpoints; `students.py` contains CRUD and SQLite logic; `static/index.html` is the Student Management UI; also includes Dockerfile and requirements |
| `dashboard/` | `server.py` reads Kubernetes API state and implements dashboard actions/demo mode; `static/index.html` is the dashboard UI; also includes Dockerfile and requirements |
| `k8s/` | `pvc.yaml`, `deployment.yaml`, `service.yaml`, `dashboard.yaml` and `dashboard-rbac.yaml` define storage, application, Service, dashboard and permissions |
| `scripts/` | PowerShell deployment/status/cleanup/test scripts and Bash helper/demo scripts |
| `tests/` | Offline unit tests, `seed_students.py`, `verify_persistence.py` and `verify_scenarios.py` |
| `docs/` | `ARCHITECTURE.md` describes design; `VERIFIED_RUN.md` records the earlier real-cluster verification run |

## ✅ Conclusion

The Student Management application was successfully designed for deployment on Kubernetes with three replicas. Startup, liveness and readiness probes are configured to monitor application initialization, process health and the ability to serve requests.

The experiment demonstrates that Kubernetes restarts a container when its liveness probe repeatedly fails, while a readiness failure only removes the pod from the Service's ready endpoints. Slow startup is handled using a startup probe, and rolling updates allow existing Ready pods to continue serving requests while new pods initialize.

A Persistent Volume Claim stores student records beyond container and pod restarts. The monitoring dashboard displays the actual cluster state and supports controlled failure and recovery demonstrations. Thus, the experiment illustrates how Kubernetes health probes improve application reliability and availability.

## 👥 Authors

_Add the team members' names and USNs here._
