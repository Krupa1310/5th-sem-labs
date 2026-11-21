# ☸️ CC Evaluation 02 - Health Checks Using Liveness and Readiness Probes

## 📑 Table of Contents

1. Problem Statement
2. Objectives
3. Kubernetes Health Probes
   - 3.1 Liveness Probe
   - 3.2 Readiness Probe
   - 3.3 Startup Probe
   - 3.4 Probe Mechanisms
   - 3.5 Probe Parameters
4. Application Implementation
   - 4.1 Flask Application
   - 4.2 Liveness and Readiness Endpoints
   - 4.3 Docker Configuration
5. Kubernetes Deployment
   - 5.1 Deployment Configuration
   - 5.2 Service Configuration
   - 5.3 Architecture
6. Execution Steps
   - 6.1 Prerequisites
   - 6.2 Environment Setup
   - 6.3 Build Docker Images
   - 6.4 Deploy to Kubernetes
   - 6.5 Access the Dashboard
7. Failure Scenarios and Testing
   - 7.1 Scenario A - Liveness Failure
   - 7.2 Scenario B - Readiness Failure
   - 7.3 Scenario C - Slow Start-up
8. Expected Observations
9. Performance and Health Monitoring
10. Troubleshooting
11. Project Structure
12. Conclusion
13. Author

---

## 1. Problem Statement

Kubernetes automatically manages containers and restarts failed containers. However, it cannot determine whether an application is actually functioning correctly just by checking whether its process is running.

An application may become unresponsive due to deadlocks, slow start-up, or temporary failures while its container is still running. In such situations, Kubernetes may continue sending traffic to an unhealthy application.

To solve this problem, Kubernetes provides health probes such as Liveness and Readiness probes.

This experiment implements liveness and readiness probes for a containerized Flask application deployed on Kubernetes.

The experiment demonstrates how Kubernetes:

- Automatically restarts unhealthy containers using liveness probes.
- Stops sending traffic to pods that are not ready using readiness probes.
- Handles applications with slow start-up times.
- Maintains application availability using multiple replicas.
- Monitors pod health through a live dashboard.

## 2. Objectives

- To understand the concept of Kubernetes health checks.
- To understand the difference between liveness, readiness, and startup probes.
- To configure HTTP-based liveness and readiness probes.
- To deploy a Flask application using Docker containers.
- To deploy three replicas of an application using Kubernetes Deployment.
- To configure a Kubernetes Service for load balancing.
- To simulate application failures and observe Kubernetes behaviour.
- To demonstrate automatic container restarts using liveness probes.
- To demonstrate traffic removal using readiness probes.
- To simulate a 30-second application start-up delay.
- To monitor pod status, restart count, and Service endpoints.
- To develop a live monitoring dashboard for Kubernetes health checks.

## 3. Kubernetes Health Probes

Kubernetes provides health probes to monitor the condition of containers running inside pods.

The kubelet periodically checks the application endpoints and takes appropriate actions based on the probe results.

### 3.1 Liveness Probe

A Liveness Probe determines whether an application inside a container is still functioning correctly.

If the liveness probe continuously fails, Kubernetes kills the container and restarts it automatically.

**Endpoint:** `/healthz`

**Behaviour:**
- Returns HTTP 200 when the application is healthy.
- Returns HTTP 500 when a liveness failure is simulated.
- Kubernetes restarts the container after the configured failure threshold is reached.

**Example:**

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

### 3.2 Readiness Probe

A Readiness Probe determines whether an application is ready to receive incoming traffic.

If the readiness probe fails, Kubernetes removes the pod from the Service endpoints.

The container continues running and is not restarted.

**Endpoint:** `/ready`

**Behaviour:**
- Returns HTTP 200 when the application is ready.
- Returns HTTP 503 when a readiness failure is simulated.
- Kubernetes removes the pod from the ready Service endpoints.
- The pod is automatically added back when it becomes healthy.

**Example:**

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 5000
  initialDelaySeconds: 3
  periodSeconds: 5
```

### 3.3 Startup Probe

A Startup Probe determines whether an application has completed its initial start-up process.

It is useful for applications that require a long time to initialize.

Until the startup probe succeeds, Kubernetes does not execute the configured liveness and readiness probes.

In this experiment, a 30-second slow start-up scenario is demonstrated using the readiness endpoint.

A separate startup probe is discussed as an alternative for applications requiring longer initialization periods.

### 3.4 Probe Mechanisms

Kubernetes supports different mechanisms for performing health checks.

| Probe Mechanism | Description |
|---|---|
| HTTP GET | Checks an HTTP endpoint and validates the response status code. |
| TCP Socket | Checks whether a specified port accepts a connection. |
| Exec | Executes a command inside the container and checks its exit status. |
| gRPC | Checks the health status of a gRPC application. |

This experiment uses HTTP GET probes because the application is a Flask-based web application.

### 3.5 Probe Parameters

The following parameters control the behaviour of Kubernetes health probes.

| Parameter | Description | Configuration |
|---|---|---|
| initialDelaySeconds | Time to wait before the first probe | 5 seconds (liveness), 3 seconds (readiness) |
| periodSeconds | Interval between consecutive probes | 5 seconds |
| timeoutSeconds | Maximum time to wait for a response | Kubernetes default: 1 second |
| failureThreshold | Consecutive failures required before action | 3 |
| successThreshold | Consecutive successes required for recovery | 1 |

With a period of 5 seconds and a failure threshold of 3, Kubernetes generally detects a persistent failure in approximately 15 seconds.

---

## 4. Application Implementation

### 4.1 Flask Application

A Python Flask application is developed to demonstrate Kubernetes health checks.

The application runs inside a Docker container and listens on port 5000.

The application provides endpoints for health monitoring, application information, and failure simulation.

The application supports:

- Liveness health checking.
- Readiness health checking.
- Application information retrieval.
- Simulated liveness failure.
- Simulated readiness failure.
- Application health restoration.
- Container crash simulation.
- Configurable start-up delay.

### 4.2 Liveness and Readiness Endpoints

The Flask application provides the following endpoints.

| Endpoint | Method | Purpose |
|---|---|---|
| `/healthz` | GET | Checks application liveness. |
| `/ready` | GET | Checks application readiness. |
| `/whoami` | GET | Identifies the application pod. |
| `/info` | GET | Returns application and health information. |
| `/control/liveness` | POST | Triggers a liveness failure. |
| `/control/readiness` | POST | Triggers a readiness failure. |
| `/control/reset` | POST | Restores application health. |
| `/crash` | POST | Simulates an application crash. |

**HTTP Response Behaviour**

| Condition | Endpoint | HTTP Status |
|---|---|---|
| Application healthy | `/healthz` | 200 OK |
| Liveness failure | `/healthz` | 500 Internal Server Error |
| Application ready | `/ready` | 200 OK |
| Readiness failure | `/ready` | 503 Service Unavailable |
| Application starting | `/ready` | 503 Service Unavailable |

### 4.3 Docker Configuration

Docker is used to package the Flask application and its dependencies into a container image.

**Application Docker Image**

```text
health-demo:1.0
```

**Dashboard Docker Image**

```text
health-dashboard:1.0
```

The application Dockerfile uses Python 3.12 slim as the base image and installs Flask 3.0.3.

Docker provides a consistent environment for running the application inside Kubernetes.

---

## 5. Kubernetes Deployment

### 5.1 Deployment Configuration

Kubernetes Deployment manages the application pods and maintains the desired number of replicas.

In this experiment, three replicas of the Flask application are deployed.

**Configuration**

| Parameter | Value |
|---|---|
| Deployment Name | health-demo |
| Number of Replicas | 3 |
| Container Name | health-demo |
| Docker Image | health-demo:1.0 |
| Container Port | 5000 |
| Liveness Endpoint | /healthz |
| Readiness Endpoint | /ready |
| Liveness Initial Delay | 5 seconds |
| Readiness Initial Delay | 3 seconds |
| Probe Period | 5 seconds |
| Failure Threshold | 3 |

The Deployment also uses rolling update settings:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 100%
    maxUnavailable: 0
```

These settings allow new pods to start while the existing healthy pods continue serving traffic.

### 5.2 Service Configuration

A Kubernetes Service provides a stable network endpoint for accessing the application pods.

**Service Name:** `health-demo-svc`

**Service Type:** NodePort

**Configuration**

| Parameter | Value |
|---|---|
| Service Name | health-demo-svc |
| Service Type | NodePort |
| Service Port | 30080 |
| Target Port | 5000 |
| Backend | health-demo pods |

The Service automatically forwards requests only to ready pods.

When a pod fails its readiness probe, its IP address is removed from the ready Service endpoints.

### 5.3 Architecture

The following architecture illustrates the working of the Kubernetes health-check system.

```text
                  Browser
                     |
                     v
             Health Dashboard
                     |
                     v
               Kubernetes API
                     |
          -------------------------
          |           |           |
          v           v           v
        Pod 1       Pod 2       Pod 3
          |           |           |
       Flask       Flask       Flask
       App         App         App
          |           |           |
      /healthz    /healthz    /healthz
       /ready      /ready      /ready
          |           |           |
          -------------------------
                     |
                     v
              Kubernetes Service
                     |
                     v
               Ready Pods Only

              Kubelet Monitoring
                     |
             ----------------
             |              |
             v              v
        Liveness         Readiness
          Probe            Probe
             |              |
        Restart Pod    Remove from
                       Service Endpoints
```

**Architecture Description**

1. The browser accesses the health monitoring dashboard.
2. The dashboard communicates with the Kubernetes API.
3. Kubernetes manages three replicas of the Flask application.
4. The kubelet periodically checks the `/healthz` and `/ready` endpoints.
5. Liveness failures cause automatic container restarts.
6. Readiness failures remove pods from Service endpoints.
7. The Kubernetes Service forwards requests only to ready pods.
8. The dashboard displays real-time pod health information.

---

## 6. Execution Steps

### 6.1 Prerequisites

The following software and tools are required:

| Software | Purpose |
|---|---|
| Docker Desktop | Building and running container images |
| Kubernetes | Container orchestration |
| kubectl | Managing Kubernetes resources |
| Python 3 | Running optional automated tests |
| Flask | Developing the web application |
| Web Browser | Accessing the monitoring dashboard |

A local Kubernetes cluster can be created using:

- Docker Desktop Kubernetes
- Minikube
- Kind

### 6.2 Environment Setup

Start Docker Desktop and enable Kubernetes.

Verify Docker installation:

```bash
docker --version
```

Verify Kubernetes installation:

```bash
kubectl version --client
```

Check cluster connectivity:

```bash
kubectl cluster-info
```

Navigate to the project directory:

```bash
cd k8s-health-probes
```

Execute the environment verification script:

```bash
bash scripts/check-env.sh
```

This script checks Docker availability, kubectl installation, and Kubernetes cluster connectivity.

### 6.3 Build Docker Images

Build the Flask application image:

```bash
docker build -t health-demo:1.0 app
```

Build the dashboard image:

```bash
docker build -t health-dashboard:1.0 dashboard
```

Verify the generated images:

```bash
docker images
```

For Minikube, load the images into the cluster:

```bash
minikube image load health-demo:1.0
minikube image load health-dashboard:1.0
```

For Kind, use:

```bash
kind load docker-image health-demo:1.0 health-dashboard:1.0
```

Docker Desktop Kubernetes generally shares the locally built images with the cluster, depending on its configuration.

### 6.4 Deploy to Kubernetes

Execute the deployment script:

```bash
bash scripts/deploy.sh
```

The deployment script performs the following operations:

1. Builds the application Docker image.
2. Builds the dashboard Docker image.
3. Loads the images into the Kubernetes cluster when required.
4. Creates the application Deployment.
5. Creates the Kubernetes Service.
6. Configures dashboard permissions using RBAC.
7. Deploys the monitoring dashboard.
8. Waits for the Kubernetes resources to become available.

Verify the deployed pods:

```bash
kubectl get pods
```

Check the Deployment:

```bash
kubectl get deployments
```

Check the Service:

```bash
kubectl get services
```

Check Service endpoints:

```bash
kubectl get endpoints health-demo-svc
```

### 6.5 Access the Dashboard

Execute:

```bash
bash scripts/open-dashboard.sh
```

Open the following URL in a browser:

```text
http://localhost:8080
```

The dashboard provides:

- Live pod status.
- Liveness probe status.
- Readiness probe status.
- Container restart count.
- Service endpoint information.
- Application health information.
- Failure simulation buttons.
- Application health restoration.
- Service traffic testing.

The dashboard automatically refreshes its information every 2 seconds.

---

## 7. Failure Scenarios and Testing

Three scenarios are implemented to demonstrate the behaviour of Kubernetes health probes.

### 7.1 Scenario A - Liveness Failure

**Objective:** Demonstrate automatic container restart when the liveness probe fails.

**Execution Steps**

1. Open the monitoring dashboard.
2. Select a target application pod.
3. Click the **Trigger Liveness Failure** button.
4. The `/healthz` endpoint starts returning HTTP 500.
5. Kubernetes detects consecutive liveness probe failures.
6. After the configured failure threshold is reached, Kubernetes terminates and restarts the container.
7. The container restart count increases by one.
8. The application starts again and returns to a healthy state.

**Expected Observation**

| Parameter | Before Failure | After Failure |
|---|---|---|
| Pod Status | Running | Running after restart |
| READY | 1/1 | Temporarily 0/1, then 1/1 |
| Liveness | Passing | Failing, then Passing |
| Restart Count | 0 | Increases by 1 |
| Application | Healthy | Automatically recovers |

**Kubernetes Commands**

```bash
kubectl get pods -w
```

```bash
kubectl describe pod <pod-name>
```

```bash
kubectl logs <pod-name> --previous
```

**Observation**

When the liveness probe continuously fails, Kubernetes automatically restarts the unhealthy container.

The restart count increases, and the application recovers after restarting.

### 7.2 Scenario B - Readiness Failure

**Objective:** Demonstrate how Kubernetes stops forwarding traffic to pods that are not ready.

**Execution Steps**

1. Open the monitoring dashboard.
2. Select a target application pod.
3. Click the **Trigger Readiness Failure** button.
4. The `/ready` endpoint starts returning HTTP 503.
5. Kubernetes detects consecutive readiness probe failures.
6. The pod changes from READY 1/1 to 0/1.
7. The pod remains in Running state.
8. The restart count remains unchanged.
9. The pod IP is removed from the ready Service endpoints.
10. Restore the application health to add the pod back to the Service.

**Expected Observation**

| Parameter | Before Failure | After Failure |
|---|---|---|
| Pod Status | Running | Running |
| READY | 1/1 | 0/1 |
| Readiness | Passing | Failing |
| Restart Count | 0 | 0 |
| Service Endpoint | Included | Removed |
| Application | Healthy | Running but not ready |

**Kubernetes Commands**

```bash
kubectl get pods -w
```

```bash
kubectl get endpoints health-demo-svc
```

```bash
kubectl describe pod <pod-name>
```

**Observation**

The readiness probe prevents an unhealthy or unavailable application pod from receiving new Service traffic.

Unlike the liveness probe, readiness failure does not restart the container.

### 7.3 Scenario C - Slow Start-up

**Objective:** Demonstrate how Kubernetes handles applications that require additional time to become ready.

**Execution Steps**

1. Open the monitoring dashboard.
2. Click the **Simulate Slow Startup** button.
3. The application start-up delay is configured to 30 seconds.
4. Kubernetes performs a rolling update of the Deployment.
5. New pods are created with the configured start-up delay.
6. The new pods remain Running but NotReady during initialization.
7. The readiness endpoint returns HTTP 503 during the delay.
8. The Service continues sending traffic to the existing healthy pods.
9. After approximately 30 seconds, the new pods become ready.
10. The new pods are added to the Service endpoints.
11. The older pods are terminated after the replacement pods become ready.

**Expected Observation**

| Parameter | During Start-up | After Start-up |
|---|---|---|
| Pod Status | Running | Running |
| READY | 0/1 | 1/1 |
| Readiness | Failing | Passing |
| Restart Count | 0 | 0 |
| Service Endpoint | Not Included | Included |
| Start-up Delay | 30 seconds | Completed |

**Kubernetes Commands**

```bash
kubectl get pods -w
```

```bash
kubectl get endpoints health-demo-svc
```

Check the Deployment rollout:

```bash
kubectl rollout status deployment/health-demo
```

**Observation**

During slow start-up, the new pods do not receive traffic until they successfully pass the readiness probe.

The existing healthy pods continue serving requests, maintaining application availability during the rolling update.

---

## 8. Expected Observations

The following table summarizes the expected behaviour of Kubernetes during the three failure scenarios.

| Scenario | Pod Status | READY | Restart Count | Service Endpoints |
|---|---|---|---|---|
| Healthy Application | Running | 1/1 | 0 | Included |
| Liveness Failure | Restarted, then Running | 1/1 after recovery | Increases by 1 | Re-added after recovery |
| Readiness Failure | Running | 0/1 | Unchanged | Removed |
| Slow Start-up | Running | 0/1 initially | 0 | Excluded until ready |

### Key Observations

**1. Liveness Probe**

When an application becomes unhealthy, Kubernetes automatically restarts the container.

**2. Readiness Probe**

When an application cannot serve traffic, Kubernetes removes the pod from the ready Service endpoints without restarting it.

**3. Slow Start-up**

During application initialization, Kubernetes prevents traffic from reaching the new pod until it becomes ready.

**4. Multiple Replicas**

Running three replicas allows the Service to continue forwarding requests to healthy pods even when one pod is unavailable.

**5. Automatic Recovery**

Once the application becomes healthy again, Kubernetes automatically updates its readiness status and Service endpoints.

---

## 9. Performance and Health Monitoring

A live monitoring dashboard is developed to observe the Kubernetes cluster and application health.

The dashboard communicates with the Kubernetes API and application pods to retrieve monitoring information.

### Dashboard Features

| Feature | Description |
|---|---|
| Pod Monitoring | Displays all application pods. |
| Liveness Monitoring | Displays liveness probe status. |
| Readiness Monitoring | Displays readiness probe status. |
| Restart Monitoring | Displays container restart counts. |
| Service Monitoring | Displays ready Service endpoints. |
| Failure Simulation | Allows liveness and readiness failures to be triggered. |
| Slow Start-up | Simulates a 30-second application start-up delay. |
| Health Restoration | Restores application health. |
| Traffic Testing | Sends 30 requests through the Kubernetes Service. |

### Monitoring Architecture

```text
             Web Browser
                  |
                  v
          Health Dashboard
                  |
                  v
           Dashboard API
                  |
          ------------------
          |                |
          v                v
    Kubernetes API    Flask Pods
          |                |
          v                v
     Pod Details       Health Info
     Restart Count     /info
     Events            /healthz
     Endpoints         /ready
          |                |
          ------------------
                  |
                  v
           Live Dashboard
```

The dashboard refreshes every 2 seconds and displays the current state of the Kubernetes resources.

### Automated Verification

The project includes an automated testing script to verify all three scenarios.

Run all tests:

```bash
python tests/verify_scenarios.py
```

Run only the liveness test:

```bash
python tests/verify_scenarios.py liveness
```

Run only the readiness test:

```bash
python tests/verify_scenarios.py readiness
```

Run only the slow start-up test:

```bash
python tests/verify_scenarios.py slowstart
```

The automated tests verify the expected Kubernetes behaviour using kubectl.

The documented cluster test results report **23/23 automated checks passed** on k3s v1.30.5. The captured verification output is available in:

```text
docs/VERIFIED_RUN.md
```

Note: The Docker image build and image-loading workflow should also be verified on the target laptop before the evaluation.

---

## 10. Troubleshooting

| Problem | Possible Cause | Solution |
|---|---|---|
| Docker daemon not reachable | Docker Desktop is not running | Start Docker Desktop. |
| kubectl cluster-info fails | Kubernetes cluster is unavailable | Enable Kubernetes or start Minikube/Kind. |
| ImagePullBackOff | Kubernetes cannot access the local image | Load the Docker image into the cluster. |
| Dashboard cannot load cluster data | RBAC permissions are missing | Apply dashboard RBAC configuration. |
| Port 8080 already in use | Another process is using the port | Use port 9090 instead. |
| Liveness probe does not restart the pod immediately | Failure threshold has not been reached | Wait for consecutive probe failures. |
| Readiness failure does not immediately remove the endpoint | Kubernetes has not completed failure detection | Wait for the configured probe checks. |
| Slow start-up takes longer | Rolling update is waiting for new pods | Monitor using kubectl get pods -w. |

### Useful Kubernetes Commands

View all pods:

```bash
kubectl get pods
```

Watch pod changes:

```bash
kubectl get pods -w
```

View application logs:

```bash
kubectl logs <pod-name>
```

View previous container logs:

```bash
kubectl logs <pod-name> --previous
```

Describe a pod:

```bash
kubectl describe pod <pod-name>
```

View Service endpoints:

```bash
kubectl get endpoints health-demo-svc
```

View Deployment:

```bash
kubectl get deployments
```

Restore the application using the dashboard or CLI script:

```bash
bash scripts/demo-cli.sh restore
```

### Cleanup

To remove the Kubernetes resources created by the experiment:

```bash
bash scripts/cleanup.sh
```

---

## 11. Project Structure

The project is organized into separate directories for the application, dashboard, Kubernetes configuration, scripts, tests, and documentation.

```text
CC-evaluation2-Health Checks Using Liveness and Readiness Probes/
│
├── app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/
│   ├── server.py
│   ├── static/
│   │   └── index.html
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── VERIFIED_RUN.md
│
├── k8s-health-probes/
│   └── [Project application files, if present]
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── dashboard-rbac.yaml
│   └── dashboard.yaml
│
├── scripts/
│   ├── check-env.sh
│   ├── deploy.sh
│   ├── open-dashboard.sh
│   ├── demo-cli.sh
│   └── cleanup.sh
│
├── tests/
│   └── verify_scenarios.py
│
└── README.md
```

### Important Files

| File | Description |
|---|---|
| app/app.py | Flask application with liveness and readiness endpoints. |
| app/Dockerfile | Builds the application Docker image. |
| dashboard/server.py | Backend for the monitoring dashboard. |
| dashboard/static/index.html | Dashboard frontend. |
| k8s/deployment.yaml | Defines three application replicas and health probes. |
| k8s/service.yaml | Creates the Kubernetes Service. |
| k8s/dashboard-rbac.yaml | Configures dashboard permissions. |
| k8s/dashboard.yaml | Deploys the dashboard. |
| scripts/check-env.sh | Checks the development environment. |
| scripts/deploy.sh | Builds and deploys the application. |
| scripts/open-dashboard.sh | Opens the monitoring dashboard using port forwarding. |
| scripts/demo-cli.sh | Executes the failure scenarios through the terminal. |
| scripts/cleanup.sh | Removes the deployed resources. |
| tests/verify_scenarios.py | Performs automated scenario verification. |
| docs/ARCHITECTURE.md | Contains the detailed architecture. |
| docs/VERIFIED_RUN.md | Contains captured verification results. |

---

## 12. Conclusion

The experiment demonstrates the implementation and working of Kubernetes Liveness and Readiness probes using a containerized Flask application.

Three replicas of the application are deployed using Kubernetes Deployment and exposed through a Kubernetes Service.

The liveness probe detects application failures and automatically restarts unhealthy containers. The readiness probe prevents traffic from reaching pods that are not ready without restarting them.

A 30-second slow start-up scenario is also implemented to demonstrate how Kubernetes manages application initialization and maintains availability during rolling updates.

A live monitoring dashboard is developed to display pod status, probe health, restart counts, Service endpoints, and application information.

The project also includes automated verification of all three failure scenarios.

The experiment helps understand how Kubernetes health probes improve application reliability, automatic recovery, traffic management, and availability in a microservices environment.

## 13. Author

**Krupa Akki**

CSE (Artificial Intelligence)

K.L.E. Technological University
