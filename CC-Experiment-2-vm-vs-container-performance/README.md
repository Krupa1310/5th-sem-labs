# Performance Analysis of Virtual Machines and Containers

## Abstract

This project experimentally compares the performance of a Virtual Machine (VM) and a Docker Container under controlled and identical workloads.

The comparison focuses on CPU performance, memory performance, disk I/O, network throughput, application performance, startup time, and scalability.

The purpose of the experiment is to understand how virtualization and containerization affect system and application performance. The comparison is based on actual measurements collected during the experiments rather than assumptions.

---

## Objectives

The main objectives of this project are:

* To configure a controlled Virtual Machine environment using VMware Workstation.
* To configure a Docker container environment with controlled CPU and memory resources.
* To execute identical workloads in both environments.
* To measure CPU performance using Sysbench.
* To measure memory performance using Sysbench.
* To measure disk I/O performance using fio.
* To measure network performance using iperf3.
* To compare FastAPI application performance.
* To measure application and container startup time.
* To study application scalability under increasing workloads.
* To store raw benchmark results and processed data separately.
* To perform statistical analysis using Python.
* To generate graphs and comparison tables.
* To document the complete experiment for reproducibility.

---

## Research Questions

The experiments are designed to answer the following questions:

1. How does CPU performance differ between a VM and a container?
2. How does memory-operation performance differ between the two environments?
3. How do VM and container environments behave under sequential and random disk workloads?
4. What network throughput and retransmissions are observed?
5. How does the same FastAPI application perform in a VM and Docker container?
6. How much time is required to start the application environment?
7. How does performance change when workload and concurrency are increased?
8. What performance differences are observed from the measured experimental data?

---

## Experimental Environment

| Component            | Configuration             |
| -------------------- | ------------------------- |
| Host OS              | Windows                   |
| Hypervisor           | VMware Workstation        |
| Guest OS             | Ubuntu                    |
| Container Platform   | Docker                    |
| Programming Language | Python                    |
| CPU Benchmark        | Sysbench                  |
| Memory Benchmark     | Sysbench                  |
| Disk Benchmark       | fio                       |
| Network Benchmark    | iperf3                    |
| Application          | FastAPI                   |
| Analysis             | Pandas, NumPy, Matplotlib |

### VM Configuration

The VM uses fixed resources throughout the benchmark campaign.

* CPU: 4 vCPUs
* Memory: 8 GB RAM
* Guest OS: Ubuntu
* Virtual disk: As configured for the experiment
* Network: Fixed network mode

The actual configuration used during the experiment is documented in:

`docs/vm-configuration.txt`

### Container Configuration

The container environment uses controlled resource limits for comparison.

* CPU limit: 4 CPUs
* Memory limit: 8 GB
* Benchmark image: `vm-container-benchmark`
* Network configuration: As documented during the experiment
* Storage configuration: Documented according to the disk experiment

The same workload parameters are used for the VM and container wherever applicable.

---

## Architecture

The overall experimental workflow is:

```text
                    PERFORMANCE ANALYSIS
                            |
              +-------------+-------------+
              |                           |
       Virtual Machine              Docker Container
          Ubuntu                         Docker
              |                           |
              +-------------+-------------+
                            |
                     Same Workloads
                            |
          +---------+-------+-------+---------+
          |         |       |       |         |
         CPU     Memory    Disk   Network   API
          |         |       |       |         |
          +---------+-------+-------+---------+
                            |
                  Startup & Scalability
                            |
                     Result Collection
                            |
                  Python Statistical Analysis
                            |
                    Graphs and Tables
                            |
                     Final Comparison
```

---

## Methodology

The experiment follows a controlled comparison methodology.

The same workload parameters are used in the VM and container environments wherever applicable. CPU and memory resources are kept fixed to reduce the effect of changing resource allocation.

Each benchmark produces raw output that is stored in the `results/raw/` directory.

Processed numerical values are stored in `results/processed/`.

Graphs generated from the measured values are stored in `results/figures/`.

The experiment therefore maintains three levels of data:

1. **Raw results** — original benchmark outputs.
2. **Processed results** — structured CSV data used for analysis.
3. **Figures** — graphs generated from the processed measurements.

---

## CPU Experiment

### Tool

Sysbench

### Workload

Prime number calculation.

### Parameters

* Maximum prime: 20000
* Threads: 1, 2, 4 and 8
* Duration: 30 seconds
* Repetitions: Multiple runs

### Metrics

* Events per second
* Execution time
* Performance variation

The CPU experiment is performed in both the VM and container environments using the same workload parameters.

The raw results are stored under:

```text
results/raw/cpu/
```

The processed CPU data is stored in:

```text
results/processed/cpu_results.csv
```

---

## Memory Experiment

### Tool

Sysbench

### Workload

Memory operations.

### Parameters

* Memory block size: 1 MB
* Total memory workload: 10 GB
* Threads: 4
* Multiple repetitions

### Metrics

* Memory operations per second
* Execution time
* Latency

The 10 GB value represents the benchmark workload size and is not the physical memory usage of the system.

Raw memory results are maintained under:

```text
results/raw/memory/
```

---

## Disk I/O Experiment

### Tool

fio

The disk experiment evaluates both sequential and random access patterns.

### Workloads

* Sequential write
* Sequential read
* Random read
* Random write

### Parameters

* Test file size: 2 GB
* Sequential block size: 1 MB
* Random block size: 4 KB
* I/O depth: 16
* Runtime: 30 seconds
* Direct I/O: enabled

### Metrics

* Throughput
* IOPS
* Latency

The container experiment uses a mounted benchmark directory so that the storage location and workload can be documented consistently.

Raw disk results are stored under:

```text
results/raw/disk/
```

---

## Network Experiment

### Tool

iperf3

The network experiment measures network throughput and retransmissions.

The experiment uses an iperf3 client-server arrangement and records the network configuration used.

### Tests

* Single-stream test
* Four parallel-stream test

### Metrics

* Network throughput
* Retransmissions
* Test duration

Raw network results are stored under:

```text
results/raw/network/
```

The network mode used during the experiment is documented because NAT, bridged networking, and other configurations can affect network measurements.

---

## Application Experiment

### Application

FastAPI

The same FastAPI application is executed in the VM and Docker environments.

The application contains three endpoints:

* `/health` — basic health check
* `/compute` — performs CPU-intensive computation
* `/memory` — creates a memory workload

The application source code is located at:

```text
api/main.py
```

The Python dependencies are located at:

```text
api/requirements.txt
```

The application Dockerfile is located at:

```text
api/Dockerfile
```

### Application Metrics

The API is tested using Apache Benchmark (`ab`) and optionally `wrk`.

The important measurements include:

* Requests per second
* Time per request
* Latency
* Failed requests
* Concurrency behavior

Identical request counts and concurrency levels are used for VM and container comparisons.

---

## Startup-Time Experiment

Startup performance is measured to understand how quickly the application environment can be created and started.

The experiment measures container startup using Docker commands and records the observed execution time.

Multiple repetitions can be performed because startup time may vary between runs.

The measurements include:

* Container startup time
* Application readiness where measurable

The final comparison uses the actual measured values from the experiment.

---

## Scalability Experiment

Scalability is evaluated by increasing the workload and concurrency.

### CPU Scalability

CPU tests are performed using:

```text
1 thread
2 threads
4 threads
8 threads
```

### API Scalability

The FastAPI application is tested using increasing thread and connection combinations.

The experiment records:

* Requests per second
* Latency
* Failed requests
* Behavior under increasing concurrency

The purpose is to observe how performance changes as workload demand increases.

---

## Results

The final results are based only on measurements collected during the experiments.

The processed results are stored in:

```text
results/processed/
```

The graphs are stored in:

```text
results/figures/
```

Important comparison metrics include:

| Metric             |       VM | Container | Difference |
| ------------------ | -------: | --------: | ---------: |
| CPU Performance    | Measured |  Measured | Calculated |
| Memory Performance | Measured |  Measured | Calculated |
| Sequential Read    | Measured |  Measured | Calculated |
| Sequential Write   | Measured |  Measured | Calculated |
| Random Read        | Measured |  Measured | Calculated |
| Random Write       | Measured |  Measured | Calculated |
| Network Throughput | Measured |  Measured | Calculated |
| Startup Time       | Measured |  Measured | Calculated |
| API Requests/sec   | Measured |  Measured | Calculated |
| API Latency        | Measured |  Measured | Calculated |

Only metrics that were actually measured in both environments should be directly compared.

---

## Statistical Analysis

Python is used to process the benchmark results.

The analysis can calculate:

* Mean
* Median
* Minimum
* Maximum
* Standard deviation

The mean represents the average performance across repeated measurements.

The median helps understand the typical result when some measurements are unusually high or low.

Standard deviation indicates the variation between repeated measurements.

Analysis scripts are maintained in:

```text
scripts/
```

---

## VM vs Container Comparison

The VM and container environments are compared using the actual experimental measurements.

For throughput-based metrics, the percentage difference can be calculated using:

```text
Difference (%) =
((Container value - VM value) / VM value) × 100
```

For execution-time measurements, the appropriate time-based comparison formula is used.

The same formula is applied consistently to comparable measurements.

The results are interpreted using the measured data rather than assuming beforehand that either virtualization method will always perform better.

---

## Discussion

The experimental results are analyzed by considering:

* CPU behavior
* Memory behavior
* Storage performance
* Network behavior
* Application throughput
* Application latency
* Startup time
* Scalability

Differences between the VM and container may be influenced by virtualization overhead, resource allocation, storage configuration, networking configuration, workload characteristics, and system background activity.

Therefore, the final discussion is based on the measurements collected during the experiment.

---

## Limitations

The experiment has several limitations:

* Results depend on the hardware used for the experiment.
* Background processes can affect benchmark measurements.
* Storage performance can vary between runs.
* Network results depend on the selected network configuration.
* A limited number of workloads cannot represent every real-world application.
* Results from one machine cannot automatically be generalized to all VM and container environments.
* Benchmark results may vary slightly between repeated executions.

---

## Conclusion

This project provides an experimental comparison of Virtual Machines and Docker Containers using controlled workloads.

CPU, memory, disk, network, application, startup, and scalability experiments are used to collect performance measurements.

The final conclusions are based on the measured benchmark results, repeated observations, statistical analysis, and documented experimental configuration.

The project also maintains raw data, processed data, scripts, graphs, and documentation so that the experiments can be reproduced.

---

## Future Work

Possible extensions of this project include:

* Testing additional workloads.
* Testing different CPU and memory allocations.
* Testing different storage configurations.
* Comparing additional container networking modes.
* Running larger application workloads.
* Testing multiple containers.
* Extending the experiment to Kubernetes.
* Studying container replicas and autoscaling.
* Automating the complete benchmark and analysis workflow.

---

## Reproduction Instructions

Clone the repository and move into the project directory:

```bash
git clone https://github.com/Krupa1310/vm-vs-container-performance.git
cd vm-vs-container-performance
```

The main project directories are:

```text
docs/                 Documentation
docker/               General benchmark Dockerfile
api/                  FastAPI application
scripts/              Benchmark and analysis scripts
workloads/            Workload files
results/raw/          Raw benchmark results
results/processed/    Processed CSV results
results/figures/      Generated graphs
```

Before running commands that use relative paths, move to the project root:

```bash
cd ~/vm-vs-container-performance
```

The project should maintain a single Git repository at the project root.

---

## Project Structure

```text
vm-vs-container-performance/
│
├── README.md
├── .gitignore
│
├── docs/
│   ├── cpu-info.txt
│   ├── memory-info.txt
│   ├── storage-info.txt
│   ├── kernel-info.txt
│   └── vm-configuration.txt
│
├── docker/
│   └── Dockerfile
│
├── api/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── workloads/
│   ├── cpu/
│   ├── memory/
│   ├── disk/
│   └── network/
│
├── scripts/
│   ├── run_cpu.sh
│   ├── analyze_results.py
│   └── generate_plots.py
│
└── results/
    ├── raw/
    ├── processed/
    └── figures/
```

---

## GitHub

The complete project is maintained in GitHub:

**Repository:** `Krupa1310/vm-vs-container-performance`

Git is used to maintain the development history of the experiment.

Important stages are committed progressively, for example:

```text
Initial project setup
Add CPU benchmark
Add memory benchmark
Add disk I/O benchmark
Add network benchmark
Add FastAPI workload
Add performance analysis
Add benchmark graphs
Update README
```

The repository contains the project documentation, source files, benchmark results, processed data, and generated figures required to understand and reproduce the experiment.
