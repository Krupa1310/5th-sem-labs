# ☸️ CC Experiment 04 - Kubernetes Resource Allocation, Scheduling & Load Balancing

## 📑 Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Aim](#2-aim)
3. [Requirements](#3-requirements)
4. [Step-by-Step Procedure](#4-step-by-step-procedure)
5. [Observation Table](#5-observation-table)
6. [Expected Learning Outcomes](#6-expected-learning-outcomes)
7. [Result](#7-result)
8. [Suggested Practical Extension](#8-suggested-practical-extension)
9. [Screenshots](#9-screenshots)
10. [Author](#10-author)

---

## 1. Problem Statement

Kubernetes provides mechanisms for allocating resources to containers, scheduling pods across cluster nodes, scaling applications, and distributing network traffic through Services.

This experiment analyzes resource allocation, pod scheduling, and Service-based load balancing in an existing three-node Kubernetes cluster. An Nginx application is deployed with six replicas, configured with CPU and memory requests and limits, and then scaled to twelve replicas.

The pod distribution, resource utilization, Service endpoints, and application accessibility are observed to understand how Kubernetes manages workloads in a cluster.

---

## 2. Aim

To analyze resource allocation, pod scheduling, and load balancing in an existing three-node Kubernetes cluster by deploying applications, configuring CPU and memory requests and limits, observing pod distribution, and testing Service load balancing.

---

## 3. Requirements

- An existing three-node Kubernetes cluster.
- `kubectl` configured and connected to the cluster.
- Internet connectivity to download container images.
- PowerShell or a terminal.
- Metrics Server installed for resource monitoring.

---

## 4. Step-by-Step Procedure

### Step 1: Verify the Kubernetes Cluster

Command:

```bash
kubectl get nodes -o wide
```

**Observations:**

- Displays all nodes available in the Kubernetes cluster.
- Verify that all three nodes are in the Ready state.
- Note down the node names.

### Step 2: Analyze Available Resources

Command:

```bash
kubectl top nodes
```

**Observations:**

- Displays CPU and memory utilization of each node.
- Compare resource utilization across all three nodes.
- If metrics are unavailable, check whether Metrics Server is installed:

```bash
kubectl get deployment metrics-server -n kube-system
```

### Step 3: Create a Deployment

Create a file named `deployment.yaml` and add the following configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resource-demo
spec:
  replicas: 6
  selector:
    matchLabels:
      app: resource-demo
  template:
    metadata:
      labels:
        app: resource-demo
    spec:
      containers:
      - name: nginx
        image: nginx
        resources:
          requests:
            cpu: "100m"
            memory: "64Mi"
          limits:
            cpu: "200m"
            memory: "128Mi"
```

Apply the configuration:

```bash
kubectl apply -f deployment.yaml
```

**Observations:**

- Creates a Deployment with six replicas, each running an Nginx container.
- A CPU request of 100m represents 0.1 CPU core.
- The memory request is 64 MiB.
- CPU and memory limits define the maximum resources the container may consume.
- The Kubernetes scheduler uses resource requests when deciding where to place pods.

### Step 4: Analyze Pod Scheduling

Commands:

```bash
kubectl get pods -o wide
```

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

**Observations:**

- The NODE column identifies the node hosting each pod.
- Observe how the six pods are distributed across the three nodes.
- Scheduling depends on available resources, node conditions, and scheduling constraints.
- Events provide information about successful scheduling or scheduling failures.

### Step 5: Analyze Resource Allocation

Commands:

```bash
kubectl describe nodes
```

```bash
kubectl top pods
```

**Observations:**

- Node details show CPU and memory capacity and allocated resources.
- Review the allocated-resource section to understand requested resources on each node.
- The top command displays current pod CPU and memory consumption.

### Step 6: Test Pod Distribution with More Replicas

Scale the Deployment from six to twelve replicas:

```bash
kubectl scale deployment resource-demo --replicas=12
```

View the pods:

```bash
kubectl get pods -o wide
```

**Observations:**

- Increases the number of replicas from six to twelve.
- Kubernetes schedules the additional pods according to available resources and scheduling constraints.
- Compare the new pod distribution with the six-replica Deployment.

### Step 7: Create a Kubernetes Service for Load Balancing

Create a file named `service.yaml` and add the following configuration:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  selector:
    app: resource-demo
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
```

Apply the configuration:

```bash
kubectl apply -f service.yaml
```

**Observations:**

- Creates a NodePort Service that selects pods with the label `app: resource-demo`.
- Port 30080 is exposed on cluster nodes, subject to cluster networking and firewall rules.
- The Service forwards connections to eligible backend pod endpoints.
- Kubernetes Service load balancing distributes connections across available endpoints; it does not guarantee equal request counts per pod.

### Step 8: Verify Load-Balancing Endpoints

Commands:

```bash
kubectl get services
```

```bash
kubectl get endpoints nginx-service
```

```bash
kubectl get endpointslices
```

**Observations:**

- Displays the Service and its assigned port.
- Endpoints and EndpointSlices show the pod IP addresses registered as backends.
- Check that the expected healthy application pods are registered.

### Step 9: Test the Application

Open a browser and enter the following address, replacing NODE-IP with an IP address reachable from your computer:

```text
http://NODE-IP:30080
```

**Observations:**

- Accesses the Nginx application through the NodePort Service.
- The Service forwards the connection to an available backend pod.
- If permitted by the cluster network, test using the IP addresses of different nodes.
- A successful page response confirms application access through the Service, but does not by itself prove equal traffic distribution.

### Step 10: Observe Resource Utilization Again

Commands:

```bash
kubectl top nodes
```

```bash
kubectl top pods
```

**Observations:**

- Observe CPU and memory utilization after increasing the replicas.
- Compare resource consumption before and after scaling.
- Identify which nodes host the workloads and compare their utilization.
- Pod placement and actual CPU or memory usage are different measurements.

### Step 11: Clean Up Resources

Delete the Service:

```bash
kubectl delete service nginx-service
```

Delete the Deployment:

```bash
kubectl delete deployment resource-demo
```

**Observations:**

- Deletes the Service and Deployment created for this experiment.
- The associated pods are removed.
- The existing three-node cluster remains intact.

---

## 5. Observation Table

| Experiment | Observation to Record |
|---|---|
| Cluster verification | Status of all three nodes |
| Initial resource utilization | CPU and memory usage of each node |
| Six replicas | Number of pods scheduled on each node |
| Twelve replicas | Updated pod distribution across nodes |
| Resource allocation | CPU and memory requests and limits |
| Load balancing | Service backend endpoints and application response |
| Final utilization | CPU and memory usage after scaling |

---

## 6. Expected Learning Outcomes

- Understand how Kubernetes allocates CPU and memory resources.
- Understand resource requests and limits.
- Observe how the Kubernetes scheduler assigns pods to nodes.
- Analyze how scaling affects pod distribution.
- Understand how Kubernetes Services distribute connections across backend pods.
- Monitor node and pod resource utilization.

---

## 7. Result

Resource allocation, pod scheduling, and Service-based load balancing were analyzed using the existing three-node Kubernetes cluster.

An Nginx Deployment was configured with CPU and memory requests and limits, scaled from six to twelve replicas, and exposed using a NodePort Service. Pod distribution, resource utilization, and Service endpoints were observed.

---

## 8. Suggested Practical Extension

Increase the CPU request in the Deployment and observe what happens when the cluster does not have enough allocatable CPU to schedule a pod.

Use the following commands to inspect a Pending pod and its scheduling events:

```bash
kubectl get pods -o wide
```

```bash
kubectl describe pod POD-NAME
```

This demonstrates resource-based scheduling constraints in Kubernetes.

---

## 9. Screenshots

Screenshots captured during the practical execution are stored in the `screenshots/` directory.

The screenshots include:

- Three-node Kubernetes cluster verification.
- Node CPU and memory utilization.
- Deployment creation.
- Pod scheduling and node distribution.
- Resource allocation details.
- Scaling from six to twelve replicas.
- NodePort Service creation.
- Service endpoints and EndpointSlices.
- Nginx application running in the browser.
- Final node and pod resource utilization.

---

## 10. Author

**Krupa Akki**

CSE (Artificial Intelligence)

K.L.E. Technological University
