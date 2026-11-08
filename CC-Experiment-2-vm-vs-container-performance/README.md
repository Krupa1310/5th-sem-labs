# Kubernetes Cluster Setup and Deployment using Kind on Windows

A practical implementation of a multi-node Kubernetes cluster using **Docker Desktop, Kind, and kubectl** on Windows. The experiment demonstrates cluster creation, application deployment, service exposure, replica scaling, and Kubernetes self-healing.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Problem Statement](#2-problem-statement)
- [3. Project Objectives](#3-project-objectives)
- [4. Technologies Used](#4-technologies-used)
- [5. Experimental Environment](#5-experimental-environment)
- [6. System Architecture](#6-system-architecture)
- [7. Project Structure](#7-project-structure)
- [8. Kubernetes Cluster Configuration](#8-kubernetes-cluster-configuration)
- [9. Experimental Procedure](#9-experimental-procedure)
- [10. Cluster Verification](#10-cluster-verification)
- [11. NGINX Deployment](#11-nginx-deployment)
- [12. Service Configuration](#12-service-configuration)
- [13. Scaling Experiment](#13-scaling-experiment)
- [14. Self-Healing Experiment](#14-self-healing-experiment)
- [15. Final Results](#15-final-results)
- [16. Applications of Kubernetes](#16-applications-of-kubernetes)
- [17. Conclusion](#17-conclusion)
- [18. Final Output Screenshot](#18-final-output-screenshot)
- [19. GitHub Workflow](#19-github-workflow)
- [20. Author](#20-author)

---

# 1. Project Overview

Kubernetes is an open-source container orchestration platform used to deploy, manage, and scale containerized applications.

This experiment demonstrates the creation of a multi-node Kubernetes cluster on Windows using Kind (Kubernetes in Docker).

The cluster consists of:

- One Control Plane Node
- Two Worker Nodes
- Six NGINX Application Pods

The experiment covers cluster creation, application deployment, service exposure, scaling, and self-healing.

---

# 2. Problem Statement

Managing containerized applications manually becomes difficult when multiple containers need to be deployed, monitored, and scaled.

There is a need for an orchestration platform that can manage application deployment, distribute workloads, maintain the required number of replicas, and automatically recover from failures.

### Problem Statement

> To create and manage a multi-node Kubernetes cluster using Kind and demonstrate container deployment, service exposure, replica scaling, and automatic recovery of failed application Pods.

---

# 3. Project Objectives

The major objectives are:

1. To install and configure WSL2 and Docker Desktop.
2. To install kubectl and Kind.
3. To create a Kubernetes cluster with three nodes.
4. To understand the roles of control plane and worker nodes.
5. To deploy an NGINX application using Kubernetes.
6. To verify the status of application Pods.
7. To expose the application using a Kubernetes Service.
8. To scale the application from three to six replicas.
9. To demonstrate Kubernetes self-healing by deleting a Pod.
10. To verify that Kubernetes automatically creates a replacement Pod.

---

# 4. Technologies Used

| Technology | Purpose |
|---|---|
| Windows | Host operating system |
| WSL2 | Linux environment support |
| Docker Desktop | Container runtime |
| Kind | Local Kubernetes cluster creation |
| kubectl | Kubernetes command-line management |
| Kubernetes | Container orchestration |
| NGINX | Sample web application |
| PowerShell | Command execution |
| Git | Version control |
| GitHub | Project repository |

---

# 5. Experimental Environment

The experiment was performed using the following environment.

| Component | Configuration |
|---|---|
| Host OS | Windows |
| Container Platform | Docker Desktop |
| Linux Support | WSL2 |
| Kubernetes Tool | Kind |
| Cluster Name | kind |
| Kubernetes Version | v1.37.0 |
| Number of Nodes | 3 |
| Control Plane | 1 |
| Worker Nodes | 2 |
| Application | NGINX |
| Initial Replicas | 3 |
| Final Replicas | 6 |

---

# 6. System Architecture

The overall architecture of the Kubernetes experiment is:

```text
                KUBERNETES CLUSTER
                        |
                +-------+-------+
                |               |
          CONTROL PLANE      WORKER NODES
                |               |
          Cluster Management   +----------------+
                               |                |
                         WORKER NODE 1    WORKER NODE 2
                               |                |
                           NGINX PODS       NGINX PODS
                               |                |
                               +-------+--------+
                                       |
                               KUBERNETES SERVICE
                                       |
                                  WEB ACCESS
                                       |
                              NGINX WELCOME PAGE
```

### Architecture Components

**Control Plane Node:**

Manages the Kubernetes cluster and controls scheduling and application deployment.

**Worker Nodes:**

Run the application Pods assigned by Kubernetes.

**Pods:**

The smallest deployable units in Kubernetes. Each Pod runs the NGINX container.

**Deployment:**

Maintains the desired number of application replicas.

**Service:**

Provides a stable network endpoint to access the application.

---

# 7. Project Structure

```text
CC-Experiment-3-Kubernetes/
│
├── README.md
│
├── kind-config.yaml
│
└── screenshots/
    ├── 01-docker-desktop.png
    ├── 02-docker-version.png
    ├── ...
    └── 20-self-healing.png
```

The screenshots directory contains the experimental screenshots. The final output screenshot is displayed in this README.

---

# 8. Kubernetes Cluster Configuration

Kind was used to create a multi-node Kubernetes cluster.

The configuration file `kind-config.yaml` defines one control plane and two worker nodes.

### Configuration

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4

nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

### Create Cluster

```powershell
kind create cluster --name kind --config kind-config.yaml
```

This command creates a Kubernetes cluster with three nodes using Docker containers.

---

# 9. Experimental Procedure

The experiment was performed in the following sequence:

```text
             START
                |
                v
       Install Required Tools
                |
                v
        Start Docker Desktop
                |
                v
       Create Kind Configuration
                |
                v
       Create Kubernetes Cluster
                |
                v
        Verify Cluster Nodes
                |
                v
        Deploy NGINX Application
                |
                v
        Create Kubernetes Service
                |
                v
        Scale Application Replicas
                |
                v
         Delete One Application Pod
                |
                v
       Verify Automatic Recovery
                |
                v
               END
```

---

# 10. Cluster Verification

After creating the cluster, the following commands were used to verify the Kubernetes environment.

### Check Cluster Information

```powershell
kubectl cluster-info --context kind-kind
```

### Check Nodes

```powershell
kubectl get nodes -o wide
```

### Check Docker Containers

```powershell
docker ps
```

### Check System Pods

```powershell
kubectl get pods -n kube-system
```

The cluster was successfully created with three Ready nodes:

- kind-control-plane
- kind-worker
- kind-worker2

---

# 11. NGINX Deployment

An NGINX application was deployed using a Kubernetes Deployment.

### Create Deployment

```powershell
kubectl create deployment web --image=nginx --replicas=3
```

### Verify Deployment

```powershell
kubectl get deployments
```

### Check Application Pods

```powershell
kubectl get pods -o wide
```

### Describe Deployment

```powershell
kubectl describe deployment web
```

The Deployment initially created three NGINX Pods and maintained the desired replica count.

---

# 12. Service Configuration

A Kubernetes NodePort Service was created to expose the NGINX application.

### Create Service

```powershell
kubectl expose deployment web --type=NodePort --port=80
```

### Verify Service

```powershell
kubectl get services
```

### Access Application

```powershell
kubectl port-forward service/web-service 8080:80
```

Open the following URL in a browser:

```text
http://localhost:8080
```

The NGINX welcome page confirms that the application is accessible.

---

# 13. Scaling Experiment

Kubernetes allows applications to be scaled by increasing or decreasing the number of replicas.

Initially, the application was deployed with three replicas.

The deployment was then scaled to six replicas.

### Scale Deployment

```powershell
kubectl scale deployment web --replicas=6
```

### Verify Scaling

```powershell
kubectl get deployments
```

### Check Pods

```powershell
kubectl get pods -o wide
```

**Observation:**

- Initial replicas: 3
- Final replicas: 6
- All six Pods reached the Running state.
- The Pods were scheduled across the two worker nodes.

---

# 14. Self-Healing Experiment

Kubernetes provides a self-healing mechanism to maintain the desired number of application replicas.

In this experiment, one running NGINX Pod was manually deleted.

### Delete a Pod

```powershell
kubectl delete pod web-5fc9f4bf66-6429r
```

### Verify Pod Status

```powershell
kubectl get pods -o wide
```

**Observation:**

1. One existing NGINX Pod was deleted.
2. Kubernetes detected that the number of available replicas was below the desired count.
3. The Deployment Controller created a replacement Pod.
4. The replacement Pod reached the Running state.
5. The application returned to six running replicas.

This demonstrates the self-healing capability of Kubernetes.

---

# 15. Final Results

The experiment was successfully completed.

| Experiment | Result |
|---|---|
| Docker Desktop Setup | Successful |
| Kind Cluster Creation | Successful |
| Three-Node Cluster | Successful |
| NGINX Deployment | Successful |
| Service Creation | Successful |
| Browser Access | Successful |
| Scaling from 3 to 6 Replicas | Successful |
| Pod Deletion | Successful |
| Automatic Pod Replacement | Successful |
| Final Running Replicas | 6 |

### Final Observation

The Kubernetes cluster successfully maintained six NGINX application replicas across two worker nodes. When one Pod was deleted, Kubernetes automatically created a replacement Pod and restored the desired replica count.

---

# 16. Applications of Kubernetes

Kubernetes is commonly used in:

- Containerized application deployment
- Microservices architecture
- Cloud-native applications
- Application scaling
- Load distribution
- Automatic recovery of failed containers
- Continuous deployment
- Distributed application management

---

# 17. Conclusion

This experiment demonstrated the practical implementation of a multi-node Kubernetes cluster using Kind on Windows.

A cluster containing one control plane and two worker nodes was successfully created. An NGINX application was deployed and exposed using a Kubernetes Service.

The application was scaled from three to six replicas. The self-healing experiment demonstrated that Kubernetes automatically replaces a deleted Pod and maintains the desired number of replicas.

Thus, the experiment provided practical knowledge of Kubernetes cluster management, application deployment, scaling, service exposure, and self-healing.

---

# 18. Final Output Screenshot

The following screenshot shows the final Kubernetes output after deleting one NGINX Pod and verifying that Kubernetes automatically created a replacement.

![Final Kubernetes Self-Healing Output](screenshots/20-self-healing.png)

---

# 19. GitHub Workflow

The experiment is maintained in the existing GitHub repository.

**Repository:** `5th-sem-labs`

**Project Directory:** `CC-Experiment-3-Kubernetes`

### Check Git Status

```powershell
git status
```

### Add Project Files

```powershell
git add CC-Experiment-3-Kubernetes
```

### Commit Changes

```powershell
git commit -m "Add Kubernetes Lab Experiment 3"
```

### Push to GitHub

```powershell
git push origin main
```

---

# 20. Author

## Krupa Akki

**CSE (Artificial Intelligence) Student**

GitHub: [Krupa1310](https://github.com/Krupa1310)

### Project Highlights

- Multi-node Kubernetes cluster creation
- Docker-based Kubernetes environment
- NGINX application deployment
- Kubernetes Service configuration
- Replica scaling
- Pod management
- Kubernetes self-healing
- GitHub-based project documentation

---

**Final Note:** This experiment demonstrates the basic working principles of Kubernetes orchestration using a local multi-node cluster.
