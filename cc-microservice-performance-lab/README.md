# 🐳 CONTAINERIZED MICROSERVICE PERFORMANCE ANALYSIS

# 🧪 LAB EVALUATION EXPERIMENT

## Build, Deploy and Analyze a Containerized Microservice Application Under Varying Workloads

**Application Domain:** Online Shopping
**Technology:** Python, Flask, REST API, Docker, Docker Compose
**Experiment:** Containerized Microservice Performance Analysis

---

## 📑 Table of Contents

1. [Aim](#-aim)
2. [Problem Statement](#-problem-statement)
3. [Objectives](#-objectives)
4. [Technologies and Configuration](#-technologies-and-configuration)
5. [Architecture](#-architecture)
6. [Project Structure](#-project-structure)
7. [Checkpoint 1 – Develop Microservices](#-checkpoint-1--develop-microservices)
8. [Checkpoint 2 – Containerization and Deployment](#-checkpoint-2--containerization-and-deployment)
9. [Checkpoint 3 – Inter-Service Communication](#-checkpoint-3--inter-service-communication)
10. [Checkpoint 4 – Workload Testing](#-checkpoint-4--workload-testing)
11. [Checkpoint 5 – Performance Monitoring and Analysis](#-checkpoint-5--performance-monitoring-and-analysis)
12. [Execution](#-execution)
13. [Workload Configuration](#-workload-configuration)
14. [Performance Observation Table](#-performance-observation-table)
15. [Performance Graphs](#-performance-graphs)
16. [Results and Analysis](#-results-and-analysis)
17. [Demonstration Evidence](#-demonstration-evidence)
18. [Final Workflow](#-final-workflow)
19. [Conclusion](#-conclusion)
20. [Authors](#-authors)

---

# 🎯 Aim

To develop a **microservice-based application** consisting of three independent services, containerize and deploy the services using **Docker and Docker Compose**, establish inter-service communication, generate varying workloads, monitor resource utilization, and analyze the performance of the application under different workload levels.

---

# 📌 Problem Statement

Modern applications are often developed using a **microservice architecture**, where an application is divided into multiple independent services.

In this experiment, an **Online Shopping Application** is developed using three independent microservices:

* **Order Service**
* **Product Service**
* **User Service**

Each service provides REST APIs and runs independently in its own Docker container.

The services are connected through a common Docker network. The Order Service communicates with the Product Service and User Service to process an order.

The application is then tested under different workload levels to observe:

* Response time
* Throughput
* Failed requests
* CPU utilization
* Memory utilization

The collected results are analyzed to understand how application performance changes as concurrency increases.

---

# 🎯 Objectives

The main objectives of this experiment are:

1. To design and develop a microservice-based application.
2. To implement three independent REST-based microservices.
3. To containerize each microservice using Docker.
4. To deploy all services using Docker Compose.
5. To establish communication between microservices using REST APIs.
6. To create a common Docker network for service communication.
7. To generate different workload levels.
8. To measure response time and throughput.
9. To monitor CPU and memory utilization.
10. To analyze application performance under varying workloads.

---

# 🛠️ Technologies and Configuration

| Component            | Technology / Configuration                              |
| -------------------- | ------------------------------------------------------- |
| Application Domain   | Online Shopping                                         |
| Programming Language | Python                                                  |
| Framework            | Flask                                                   |
| API Type             | REST API                                                |
| Containerization     | Docker                                                  |
| Orchestration        | Docker Compose                                          |
| Network              | Docker Bridge Network                                   |
| Order Service        | Port 5000                                               |
| Product Service      | Port 5001                                               |
| User Service         | Port 5002                                               |
| Workload             | POST `/order`                                           |
| Concurrency Levels   | 1, 2, 4, 8, 16                                          |
| Requests per Level   | 100                                                     |
| Performance Metrics  | Response Time, Throughput, Failed Requests, CPU, Memory |

---

# 🏗️ Architecture

The application consists of three independent microservices.

```text
                         CLIENT
                           |
                           |
                    POST /order
                           |
                           v
                  +----------------+
                  | Order Service  |
                  |    Port 5000   |
                  +----------------+
                    /            \
                   /              \
                  v                v
        +----------------+   +----------------+
        | Product        |   | User           |
        | Service        |   | Service        |
        | Port 5001      |   | Port 5002      |
        +----------------+   +----------------+
                  \                /
                   \              /
                    +------------+
                    Docker Network
               microservice-network
```

### Service Responsibilities

### 1. Order Service

**Port:** `5000`

Responsible for creating an order.

**Endpoint:**

```text
POST /order
```

The Order Service communicates with:

```text
http://user-service:5002/user/{user_id}
```

and

```text
http://product-service:5001/product/{product_id}
```

---

### 2. Product Service

**Port:** `5001`

Responsible for retrieving product information.

**Endpoint:**

```text
GET /product/<product_id>
```

Example:

```text
GET /product/1
```

---

### 3. User Service

**Port:** `5002`

Responsible for retrieving user information.

**Endpoint:**

```text
GET /user/<user_id>
```

Example:

```text
GET /user/1
```

---

# 📁 Project Structure

```text
cc-microservice-performance-lab/
│
├── order-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── product-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── user-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── performance-analysis/
│   └── performance_results.csv
│
├── screenshots/
│   ├── 01_microservice-performance-lab.png
│   ├── 02_product_service_api.png
│   ├── 03_User_service_api.png
│   ├── 04_Order_service_api.png
│   ├── 05_Product_docker_image.png
│   ├── 06_Docker_images.png
│   ├── 07_User_docker_image.png
│   ├── 08_Docker_images.png
│   ├── 09_Order_docker_image.png
│   ├── 10_all_docker_images.png
│   ├── 11_docker_compose_running.png
│   ├── 12_end_to_end_order_test.png
│   ├── 13_docker_ps.png
│   ├── 14_docker_network.png
│   ├── 15_docker_compose_ps.png
│   ├── 16_end_to_end_order_test_image.png
│   ├── 17_performance_test_results.png
│   ├── 18_response_time.png
│   ├── 19_Throughput.png
│   ├── 20_CPU_Usage.png
│   └── 21_Memory_usage.png
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# 1️⃣ Checkpoint 1 – Develop Microservices

Three independent microservices were developed using **Python Flask**.

| Service         | Port | Responsibility   | REST Endpoint       |
| --------------- | ---: | ---------------- | ------------------- |
| Order Service   | 5000 | Create Order     | `POST /order`       |
| Product Service | 5001 | Retrieve Product | `GET /product/<id>` |
| User Service    | 5002 | Retrieve User    | `GET /user/<id>`    |

Each service also provides a health-check endpoint:

```text
GET /health
```

### Order Service

The Order Service receives `user_id` and `product_id`.

It then requests:

```text
User Service → User information
Product Service → Product information
```

After receiving valid responses, it returns the order confirmation.

### Product Service

The Product Service contains sample product information:

```text
1 → Laptop → ₹50000
2 → Headphones → ₹2000
3 → Keyboard → ₹1500
```

### User Service

The User Service contains sample user information:

```text
1 → Monika
2 → Krupa
3 → Srujana
```

All three services were independently tested using their REST APIs.

---

# 2️⃣ Checkpoint 2 – Containerization and Deployment

Each microservice has its own Dockerfile.

### Dockerfile Structure

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE <PORT>
CMD ["python", "app.py"]
```

Separate Docker images were created for:

```text
order-service
product-service
user-service
```

Docker Compose was used to build and deploy all three services together.

---

# 3️⃣ Checkpoint 3 – Inter-Service Communication

A common Docker bridge network was created:

```text
microservice-network
```

All three services are connected to this network.

```yaml
networks:
  microservice-network:
    driver: bridge
```

Docker service names are used for communication instead of localhost.

### Order → User

```text
http://user-service:5002/user/{user_id}
```

### Order → Product

```text
http://product-service:5001/product/{product_id}
```

This allows the Order Service to communicate with the other services inside the Docker network.

### End-to-End Flow

```text
Client
  |
  v
Order Service
  |
  +------> User Service
  |
  +------> Product Service
  |
  v
Order Created Successfully
```

---

# 4️⃣ Checkpoint 4 – Workload Testing

The application was tested under different concurrency levels.

The workload was generated by sending **100 order requests** for each concurrency level.

The following concurrency levels were used:

```text
1
2
4
8
16
```

The following metrics were collected:

* Average response time
* Throughput
* Failed requests
* CPU utilization
* Memory utilization

The workload was applied to:

```text
POST /order
```

---

# 5️⃣ Checkpoint 5 – Performance Monitoring and Analysis

The performance of the application was monitored under different workloads.

CPU and memory utilization were observed for:

* Order Service
* Product Service
* User Service

The measured results were recorded in:

```text
performance-analysis/performance_results.csv
```

The results were then used to generate performance graphs.

---

# ⚙️ Execution

## Step 1 – Navigate to Project Directory

```bash
cd ~/5th-sem-labs/cc-microservice-performance-lab
```

## Step 2 – Build and Start Containers

```bash
docker compose up --build
```

## Step 3 – Verify Running Containers

```bash
docker ps
```

The following containers should be running:

```text
order-service
product-service
user-service
```

## Step 4 – Verify Docker Network

```bash
docker network ls
```

The common network should be:

```text
microservice-network
```

## Step 5 – Test Services

### Product Service

```text
GET http://localhost:5001/product/1
```

### User Service

```text
GET http://localhost:5002/user/1
```

### Order Service

```text
POST http://localhost:5000/order
```

Example request:

```json
{
  "user_id": 1,
  "product_id": 1
}
```

Expected response:

```json
{
  "message": "Order created successfully",
  "user": {
    "id": 1,
    "name": "Monika",
    "email": "monika@example.com"
  },
  "product": {
    "id": 1,
    "name": "Laptop",
    "price": 50000
  }
}
```

---

# 📊 Workload Configuration

| Parameter                | Value                                                   |
| ------------------------ | ------------------------------------------------------- |
| Workload API             | `POST /order`                                           |
| Total Requests per Level | 100                                                     |
| Concurrency 1            | 100 requests                                            |
| Concurrency 2            | 100 requests                                            |
| Concurrency 4            | 100 requests                                            |
| Concurrency 8            | 100 requests                                            |
| Concurrency 16           | 100 requests                                            |
| Metrics                  | Response Time, Throughput, Failed Requests, CPU, Memory |

---

# 📈 Performance Observation Table

| Workload     | Concurrency | Response Time (ms) | Throughput (req/s) | Failed Requests | Order CPU | Order Memory | Product CPU | Product Memory | User CPU | User Memory |
| ------------ | ----------: | -----------------: | -----------------: | --------------: | --------: | ------------ | ----------: | -------------- | -------: | ----------- |
| 100 requests |           1 |              31.78 |              31.32 |               0 |     0.26% | 57.12 MiB    |       0.25% | 47.79 MiB      |    0.22% | 48.34 MiB   |
| 100 requests |           2 |              33.99 |              58.29 |               0 |     0.20% | 56.96 MiB    |       0.20% | 47.86 MiB      |    0.10% | 48.93 MiB   |
| 100 requests |           4 |              33.05 |             118.92 |               0 |     0.42% | 57.63 MiB    |       0.16% | 47.65 MiB      |    0.15% | 49.08 MiB   |
| 100 requests |           8 |             109.12 |              71.78 |               0 |     0.22% | 58.31 MiB    |       0.37% | 47.56 MiB      |    0.23% | 48.88 MiB   |
| 100 requests |          16 |             164.93 |              90.18 |               0 |     0.17% | 58.00 MiB    |       0.24% | 48.33 MiB      |    0.13% | 48.75 MiB   |

---

# 📊 Performance Graphs

## Response Time

The graph shows how average response time changes with increasing concurrency.

![Response Time](screenshots/18_response_time.png)

---

## Throughput

The graph shows the number of requests processed per second at different concurrency levels.

![Throughput](screenshots/19_Throughput.png)

---

## CPU Utilization

The graph shows CPU utilization of the three microservices under different workloads.

![CPU Usage](screenshots/20_CPU_Usage.png)

---

## Memory Utilization

The graph shows memory utilization of the three microservices under different workloads.

![Memory Usage](screenshots/21_Memory_usage.png)

---

# 🔍 Results and Analysis

### 1. Response Time

The average response time was:

```text
Concurrency 1  → 31.78 ms
Concurrency 2  → 33.99 ms
Concurrency 4  → 33.05 ms
Concurrency 8  → 109.12 ms
Concurrency 16 → 164.93 ms
```

The response time remains almost constant up to concurrency 4.

At concurrency 8 and 16, the response time increases significantly.

Therefore, higher concurrency creates additional processing and waiting overhead.

---

### 2. Throughput

The measured throughput was:

```text
Concurrency 1  → 31.32 req/s
Concurrency 2  → 58.29 req/s
Concurrency 4  → 118.92 req/s
Concurrency 8  → 71.78 req/s
Concurrency 16 → 90.18 req/s
```

The highest throughput was obtained at:

```text
Concurrency = 4
Throughput = 118.92 requests/sec
```

This indicates that concurrency 4 provided the best observed processing efficiency.

---

### 3. Failed Requests

The number of failed requests was:

```text
Concurrency 1  → 0
Concurrency 2  → 0
Concurrency 4  → 0
Concurrency 8  → 0
Concurrency 16 → 0
```

Therefore, all workload levels completed successfully without failed requests.

---

### 4. CPU Utilization

CPU utilization remained low for all three services.

The highest observed CPU utilization was:

```text
Order Service → 0.42%
```

at concurrency 4.

The Product and User Services also maintained low CPU utilization throughout the experiment.

This indicates that CPU was not the major performance bottleneck during the tested workload.

---

### 5. Memory Utilization

The Order Service showed the highest memory consumption among the three services.

Its memory usage ranged approximately from:

```text
56.96 MiB to 58.31 MiB
```

The Product Service used approximately:

```text
47.56 MiB to 48.33 MiB
```

The User Service used approximately:

```text
48.34 MiB to 49.08 MiB
```

Therefore, the Order Service was the most memory-consuming service in the experiment.

---

### 6. Overall Performance Analysis

From the observations:

* Increasing concurrency from 1 to 4 improved throughput.
* The highest throughput was **118.92 requests/sec at concurrency 4**.
* Response time increased sharply at concurrency 8 and 16.
* No failed requests were observed.
* CPU utilization remained low.
* The Order Service consumed the highest memory.
* Higher concurrency beyond 4 did not provide proportional throughput improvement.
* The system performed best at the moderate workload level of concurrency 4.

---

# 🖼️ Demonstration Evidence

The following screenshots provide evidence of the complete experiment:

| No. | Evidence                     |
| --: | ---------------------------- |
|  01 | Microservice Performance Lab |
|  02 | Product Service API          |
|  03 | User Service API             |
|  04 | Order Service API            |
|  05 | Product Docker Image         |
|  06 | Docker Images                |
|  07 | User Docker Image            |
|  08 | Docker Images                |
|  09 | Order Docker Image           |
|  10 | All Docker Images            |
|  11 | Docker Compose Running       |
|  12 | End-to-End Order Test        |
|  13 | Docker PS                    |
|  14 | Docker Network               |
|  15 | Docker Compose PS            |
|  16 | End-to-End Order Test        |
|  17 | Performance Test Results     |
|  18 | Response Time Graph          |
|  19 | Throughput Graph             |
|  20 | CPU Usage Graph              |
|  21 | Memory Usage Graph           |

---

# 🔄 Final Workflow

```text
DEVELOP
   ↓
CONTAINERIZE
   ↓
DEPLOY
   ↓
CONNECT
   ↓
LOAD TEST
   ↓
MONITOR
   ↓
ANALYZE
   ↓
DEMONSTRATE
```

---

# ✅ Conclusion

The Online Shopping application was successfully developed using a **three-microservice architecture** consisting of Order Service, Product Service, and User Service.

All services were independently developed using Flask, containerized using Docker, and deployed using Docker Compose.

A common Docker bridge network was used to establish communication between the services. The Order Service successfully communicated with the Product and User Services to process end-to-end order requests.

The application was tested using concurrency levels of **1, 2, 4, 8, and 16** with 100 requests at each level.

The results showed that:

* **Concurrency 4 achieved the highest throughput of 118.92 requests/sec.**
* Response time increased significantly at higher concurrency levels.
* No failed requests were recorded.
* CPU utilization remained low.
* Order Service had the highest memory utilization.

Thus, the experiment successfully demonstrates how a containerized microservice application can be **developed, deployed, connected, load-tested, monitored, and analyzed under varying workloads**.

---

# 👥 Authors

1. **Monika.M. Bhandari**
2. **Krupa.Akki**
3. **Srujana.V.B**
4. **Srujana.Patil**






