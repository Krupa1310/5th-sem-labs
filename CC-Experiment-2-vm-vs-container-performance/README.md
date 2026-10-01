# Performance Analysis of Virtual Machines and Containers

A practical performance study comparing **Virtual Machines (VMs)** and **Docker Containers** under controlled and identical workloads.

---

## Table of Contents

* [1. Project Overview](#1-project-overview)
* [2. Problem Statement](#2-problem-statement)
* [3. Project Objectives](#3-project-objectives)
* [4. Research Questions](#4-research-questions)
* [5. Experimental Environment](#5-experimental-environment)

  * [5.1 Hardware Configuration](#51-hardware-configuration)
  * [5.2 Software Configuration](#52-software-configuration)
  * [5.3 VM Configuration](#53-vm-configuration)
  * [5.4 Container Configuration](#54-container-configuration)
* [6. System Architecture](#6-system-architecture)
* [7. Project Structure](#7-project-structure)
* [8. Experimental Methodology](#8-experimental-methodology)
* [9. Baseline Measurement](#9-baseline-measurement)
* [10. CPU Performance Experiment](#10-cpu-performance-experiment)
* [11. Memory Performance Experiment](#11-memory-performance-experiment)
* [12. CPU and Memory Monitoring](#12-cpu-and-memory-monitoring)
* [13. Disk I/O Performance Experiment](#13-disk-io-performance-experiment)
* [14. Network Performance Experiment](#14-network-performance-experiment)
* [15. FastAPI Application](#15-fastapi-application)
* [16. Application Performance Benchmark](#16-application-performance-benchmark)
* [17. Startup-Time Experiment](#17-startup-time-experiment)
* [18. Scalability Experiment](#18-scalability-experiment)
* [19. Automated Benchmark Execution](#19-automated-benchmark-execution)
* [20. Result Collection and Processing](#20-result-collection-and-processing)
* [21. Statistical Analysis](#21-statistical-analysis)
* [22. Performance Difference Calculation](#22-performance-difference-calculation)
* [23. Results](#23-results)

  * [23.1 CPU Results](#231-cpu-results)
  * [23.2 Memory Results](#232-memory-results)
  * [23.3 Disk Results](#233-disk-results)
  * [23.4 Network Results](#234-network-results)
  * [23.5 Application Results](#235-application-results)
  * [23.6 Startup Results](#236-startup-results)
  * [23.7 Scalability Results](#237-scalability-results)
* [24. VM vs Container Comparison](#24-vm-vs-container-comparison)
* [25. Performance Applications](#25-performance-applications)
* [26. Discussion](#26-discussion)
* [27. Limitations](#27-limitations)
* [28. Reproducibility](#28-reproducibility)
* [29. Complete Experimental Workflow](#29-complete-experimental-workflow)
* [30. Future Work](#30-future-work)
* [31. Conclusion](#31-conclusion)
* [32. GitHub Workflow](#32-github-workflow)
* [33. Author](#33-author)

---

# 1. Project Overview

Virtual Machines and Containers are two widely used approaches for deploying applications and workloads.

A Virtual Machine provides an isolated operating-system environment through a hypervisor, while a container provides process-level isolation while sharing the host operating-system kernel.

This project experimentally compares the performance of these two environments under identical workloads.

The study evaluates:

* CPU performance
* Memory performance
* Disk I/O performance
* Network performance
* Application performance
* Startup time
* Resource utilization
* Scalability under increasing workloads

The experiments use repeated measurements, raw benchmark outputs, processed CSV data, statistical analysis, and graphical visualization.

The objective is to understand the measured performance characteristics of each environment rather than assuming beforehand that one environment will always perform better.

---

# 2. Problem Statement

Virtual Machines and Containers provide isolated environments for running applications, but they differ in their virtualization and resource-management approaches.

Virtual Machines generally include a complete guest operating system, while containers share the host operating-system kernel.

These architectural differences can affect:

* CPU execution
* Memory operations
* Storage I/O
* Network throughput
* Application response time
* Startup time
* Resource utilization
* Scalability

Therefore, there is a need for a controlled experimental study that executes the same workloads in both environments and compares their measured performance.

### Problem Statement

> To experimentally evaluate and compare the performance, resource utilization, application behavior, startup time, and scalability of Virtual Machines and Docker Containers under identical workloads and controlled resource configurations.

---

# 3. Project Objectives

The major objectives of the project are:

1. To configure a controlled Virtual Machine environment.
2. To configure a controlled Docker Container environment.
3. To execute identical workloads in both environments.
4. To measure CPU performance using Sysbench.
5. To measure memory performance using Sysbench.
6. To evaluate disk I/O performance using fio.
7. To evaluate network performance using iperf3.
8. To evaluate application performance using FastAPI.
9. To measure startup and application-ready time.
10. To study scalability under increasing workloads.
11. To repeat benchmark experiments to reduce the effect of temporary fluctuations.
12. To store raw benchmark outputs separately from processed results.
13. To process benchmark data using Python and Pandas.
14. To generate comparison graphs using Matplotlib.
15. To calculate statistical measures such as mean, median, minimum, maximum, and standard deviation.
16. To summarize VM and container performance using comparison tables.
17. To maintain the complete experiment in a reproducible GitHub repository.

---

# 4. Research Questions

The experiment investigates the following questions:

1. How does CPU performance differ between a VM and a container under the same workload?
2. How do memory operations behave in the two environments?
3. How do sequential and random disk workloads differ between the environments?
4. How does network throughput vary between the VM and container configurations?
5. How does the same FastAPI application behave in both environments?
6. How does startup time differ between the two deployment environments?
7. How does each environment scale when workload intensity is increased?
8. How much variation exists between repeated benchmark executions?
9. What resource-utilization patterns are observed during the experiments?

---

# 5. Experimental Environment

## 5.1 Hardware Configuration

The experiment was conducted using the following general environment:

| Component                  | Configuration      |
| -------------------------- | ------------------ |
| Host Operating System      | Windows            |
| Hypervisor                 | VMware Workstation |
| Guest Operating System     | Ubuntu             |
| Virtualization Environment | Virtual Machine    |
| Container Platform         | Docker             |
| Programming Language       | Python             |
| CPU Benchmark              | Sysbench           |
| Disk Benchmark             | fio                |
| Network Benchmark          | iperf3             |
| Application Framework      | FastAPI            |
| Data Processing            | Pandas             |
| Visualization              | Matplotlib         |

Actual hardware and system information is recorded in the `docs/` directory.

---

## 5.2 Software Configuration

The major software tools used in the experiment were:

| Tool               | Purpose                                 |
| ------------------ | --------------------------------------- |
| Sysbench           | CPU and memory benchmarking             |
| fio                | Disk I/O benchmarking                   |
| iperf3             | Network performance measurement         |
| FastAPI            | Application workload                    |
| Uvicorn            | FastAPI application server              |
| Apache Benchmark   | HTTP performance testing                |
| wrk                | Optional HTTP scalability testing       |
| Pandas             | CSV processing and statistical analysis |
| NumPy              | Numerical analysis                      |
| Matplotlib         | Graph generation                        |
| Docker             | Container execution                     |
| VMware Workstation | Virtual machine execution               |
| Git                | Version control                         |
| GitHub             | Project publication                     |

---

## 5.3 VM Configuration

The VM was configured with fixed resources so that the same allocation could be maintained throughout the experiment.

| Resource     | Configuration      |
| ------------ | ------------------ |
| Virtual CPUs | 4                  |
| Memory       | 8 GB               |
| Virtual Disk | 60 GB              |
| Guest OS     | Ubuntu 24.04 LTS   |
| Network      | Fixed network mode |
| Hypervisor   | VMware Workstation |

The actual configuration used during the experiment is documented in:

```text
docs/vm-configuration.txt
```

System information is stored in:

```text
docs/cpu-info.txt
docs/memory-info.txt
docs/storage-info.txt
docs/kernel-info.txt
```

---

## 5.4 Container Configuration

The benchmark container was configured using explicit resource limits.

| Resource        | Container Configuration        |
| --------------- | ------------------------------ |
| CPU Limit       | 4 CPUs                         |
| Memory Limit    | 8 GB                           |
| Base Image      | Ubuntu 24.04                   |
| Benchmark Image | `vm-container-benchmark`       |
| Storage         | Mounted benchmark directory    |
| Network         | Fixed/documented configuration |

The same CPU and memory limits were maintained for controlled container experiments.

Example:

```bash
docker run --rm \
  --cpus=4 \
  --memory=8g \
  vm-container-benchmark
```

---

# 6. System Architecture

The overall experimental architecture is:

```text
                         PERFORMANCE ANALYSIS
                                  |
                 +----------------+----------------+
                 |                                 |
        VIRTUAL MACHINE                     DOCKER CONTAINER
                 |                                 |
        VMware Workstation                       Docker
                 |                                 |
             Ubuntu VM                      Container Image
                 |                                 |
                 +---------------+-----------------+
                                 |
                         SAME WORKLOADS
                                 |
          +----------------------+----------------------+
          |          |            |          |          |
         CPU       Memory        Disk      Network   Application
       Sysbench   Sysbench        fio       iperf3     FastAPI
          |          |            |          |          |
          +----------+------------+----------+----------+
                                 |
                         Result Collection
                                 |
                    +------------+------------+
                    |                         |
              Raw Benchmark Data       Processed CSV
                    |                         |
                    +------------+------------+
                                 |
                        Python Analysis
                                 |
                    +------------+------------+
                    |                         |
               Statistics                 Graphs
                    |                         |
                    +------------+------------+
                                 |
                         Final Comparison
```

### Architecture Components

**Virtual Machine:**
Runs Ubuntu as a guest operating system through VMware Workstation.

**Docker Container:**
Runs the benchmark workloads using a standardized Ubuntu-based Docker image.

**Benchmark Layer:**
Uses identical workloads and parameters wherever possible.

**Analysis Layer:**
Processes raw measurements using Python, Pandas, and Matplotlib.

**Result Layer:**
Stores raw outputs, processed CSV files, graphs, and final comparison tables.

---

# 7. Project Structure

The project follows a structured organization separating application code, benchmark scripts, documentation, and results.

```text
CC-Experiment-2-vm-vs-container-performance/
│
├── README.md
├── README-backup.md
├── .gitignore
│
├── docs/
│   ├── cpu-info.txt
│   ├── memory-info.txt
│   ├── storage-info.txt
│   ├── kernel-info.txt
│   ├── vm-configuration.txt
│   └── methodology.md
│
├── docker/
│   ├── Dockerfile
│   └── benchmark.sh
│
├── api/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── scripts/
│   ├── run_cpu.sh
│   ├── run_memory.sh
│   ├── run_disk.sh
│   ├── run_network.sh
│   ├── collect_metrics.py
│   ├── analyze_results.py
│   └── generate_plots.py
│
├── workloads/
│   ├── cpu/
│   ├── memory/
│   ├── disk/
│   └── network/
│
├── results/
│   ├── raw/
│   ├── processed/
│   └── figures/
│
└── analysis/
    └── analysis.ipynb
```

Some directories are created progressively as experiments are completed.

---

# 8. Experimental Methodology

The experiment follows a controlled and sequential methodology.

```text
Project Start
     |
     v
Prepare Environment
     |
     v
Configure VM
     |
     v
Configure Docker
     |
     v
Establish Baseline
     |
     v
CPU Benchmark
     |
     v
Memory Benchmark
     |
     v
Disk Benchmark
     |
     v
Network Benchmark
     |
     v
FastAPI Benchmark
     |
     v
Startup Test
     |
     v
Scalability Test
     |
     v
Collect Raw Data
     |
     v
Process CSV Data
     |
     v
Statistical Analysis
     |
     v
Generate Graphs
     |
     v
Comparison Tables
     |
     v
Discussion and Conclusion
     |
     v
GitHub Publication
```

To improve reliability:

* The same workload parameters are used for both environments.
* VM resources remain fixed.
* Container CPU and memory limits remain fixed.
* Experiments are repeated multiple times.
* Raw benchmark output is preserved.
* Processed data is stored separately.
* Actual measurements are used for graphs and tables.
* Results are not replaced with assumed or expected values.

---

# 9. Baseline Measurement

Before comparing the two environments, a CPU baseline was established using Sysbench.

### Workload

```bash
sysbench cpu \
  --cpu-max-prime=20000 \
  --threads=4 \
  --time=30 \
  run
```

The baseline output is stored in:

```text
results/raw/baseline/cpu.txt
```

### Purpose

The baseline provides a reference measurement for interpreting subsequent benchmark results.

---

# 10. CPU Performance Experiment

## Tool

**Sysbench**

## Workload

Prime-number calculation.

## Parameters

| Parameter        |          Value |
| ---------------- | -------------: |
| Prime maximum    |          20000 |
| Threads          |     1, 2, 4, 8 |
| Duration         |     30 seconds |
| Repetitions      |             10 |
| Primary metric   |     Events/sec |
| Secondary metric | Execution time |

### VM Execution

Example:

```bash
sysbench cpu \
  --cpu-max-prime=20000 \
  --threads=4 \
  --time=30 \
  run
```

Repeated results are stored under:

```text
results/raw/cpu/vm/
```

### Container Execution

```bash
docker run --rm \
  --cpus=4 \
  --memory=8g \
  vm-container-benchmark \
  sysbench cpu \
  --cpu-max-prime=20000 \
  --threads=4 \
  --time=30 \
  run
```

Repeated results are stored under:

```text
results/raw/cpu/container/
```

### CPU Metrics

The following metrics are analyzed:

* Events per second
* Total execution time
* Mean performance
* Median performance
* Standard deviation
* Performance at different thread counts

---

# 11. Memory Performance Experiment

Memory performance was evaluated using Sysbench.

### Parameters

| Parameter      |                      Value |
| -------------- | -------------------------: |
| Block size     |                       1 MB |
| Total workload |                      10 GB |
| Threads        |                          4 |
| Repetitions    |                         10 |
| Metrics        | Operations/sec and latency |

### VM

```bash
sysbench memory \
  --memory-block-size=1M \
  --memory-total-size=10G \
  --threads=4 \
  run
```

### Container

```bash
docker run --rm \
  --cpus=4 \
  --memory=8g \
  vm-container-benchmark \
  sysbench memory \
  --memory-block-size=1M \
  --memory-total-size=10G \
  --threads=4 \
  run
```

Raw results are stored under:

```text
results/raw/memory/
```

The experiment evaluates how memory operations behave under the two deployment environments.

---

# 12. CPU and Memory Monitoring

System resource utilization was monitored during benchmark execution.

### System Monitoring

```bash
htop
```

or:

```bash
vmstat 1
```

### Container Monitoring

```bash
docker stats
```

The monitored parameters include:

* CPU utilization
* Memory utilization
* Network I/O
* Block I/O
* Resource consumption during workload execution

Resource-utilization data is considered together with benchmark performance.

---

# 13. Disk I/O Performance Experiment

Disk performance was measured using **fio**.

Four workloads were considered:

1. Sequential write
2. Sequential read
3. Random read
4. Random write

### Benchmark File

```text
~/fio-test/testfile
```

### Sequential Write

```bash
fio --name=seq-write \
  --filename=~/fio-test/testfile \
  --size=2G \
  --bs=1M \
  --rw=write \
  --direct=1 \
  --iodepth=16 \
  --runtime=30 \
  --time_based
```

### Sequential Read

```bash
fio --name=seq-read \
  --filename=~/fio-test/testfile \
  --size=2G \
  --bs=1M \
  --rw=read \
  --direct=1 \
  --iodepth=16 \
  --runtime=30 \
  --time_based
```

### Random Read

```bash
fio --name=random-read \
  --filename=~/fio-test/testfile \
  --size=2G \
  --bs=4k \
  --rw=randread \
  --direct=1 \
  --iodepth=16 \
  --runtime=30 \
  --time_based
```

### Random Write

```bash
fio --name=random-write \
  --filename=~/fio-test/testfile \
  --size=2G \
  --bs=4k \
  --rw=randwrite \
  --direct=1 \
  --iodepth=16 \
  --runtime=30 \
  --time_based
```

### Container Disk Test

The benchmark directory is mounted into the container:

```bash
docker run --rm \
  -v ~/fio-test:/fio-test \
  vm-container-benchmark \
  fio --name=seq-write \
  --filename=/fio-test/testfile \
  --size=2G \
  --bs=1M \
  --rw=write \
  --direct=1 \
  --iodepth=16 \
  --runtime=30 \
  --time_based
```

### Disk Metrics

| Metric     | Unit |
| ---------- | ---- |
| Throughput | MB/s |
| IOPS       | IOPS |
| Latency    | ms   |

Raw disk results are stored in:

```text
results/raw/disk/
```

---

# 14. Network Performance Experiment

Network performance was measured using **iperf3**.

### Server

```bash
iperf3 -s
```

Find the server address:

```bash
ip addr
```

### Client

```bash
iperf3 -c <SERVER-IP> -t 30
```

### Parallel Streams

```bash
iperf3 -c <SERVER-IP> -t 30 -P 4
```

### Metrics

* Network throughput
* Retransmissions
* Transfer amount
* Performance using parallel streams

Raw network results are stored under:

```text
results/raw/network/
```

The same client/server arrangement and network configuration should be maintained for the VM and container measurements.

---

# 15. FastAPI Application

A FastAPI application was developed to represent a realistic application workload.

The application contains three endpoints:

### Health Endpoint

```text
GET /health
```

Returns:

```json
{
  "status": "healthy"
}
```

### Compute Endpoint

```text
GET /compute
```

Performs repeated arithmetic operations to generate CPU workload.

### Memory Endpoint

```text
GET /memory
```

Creates a large Python list to generate memory activity.

### Application Source

The application source is located at:

```text
api/main.py
```

The application uses:

```text
FastAPI
Uvicorn
Python
```

---

# 16. Application Performance Benchmark

The FastAPI application was executed in both the VM and container environments.

### Docker Image

The application image is:

```text
performance-api
```

### Build

```bash
docker build -t performance-api -f api/Dockerfile api
```

### Run

```bash
docker run --rm \
  --cpus=4 \
  --memory=8g \
  -p 8000:8000 \
  performance-api
```

### Health Test

```bash
curl http://127.0.0.1:8000/health
```

### Apache Benchmark

Install:

```bash
sudo apt install -y apache2-utils
```

Health endpoint:

```bash
ab -n 10000 -c 100 http://127.0.0.1:8000/health
```

Compute endpoint:

```bash
ab -n 1000 -c 10 http://127.0.0.1:8000/compute
```

### Application Metrics

The following metrics are collected:

| Metric              | Unit         |
| ------------------- | ------------ |
| Requests per second | requests/sec |
| Time per request    | ms           |
| Failed requests     | count        |
| Connection time     | ms           |
| Latency             | ms           |

Optional scalability testing can be performed using `wrk`.

```bash
wrk -t4 -c100 -d30s http://127.0.0.1:8000/health
```

---

# 17. Startup-Time Experiment

Startup performance was evaluated for the application environment.

The measurements consider:

* Environment startup
* Application startup
* Application-ready time

A controlled Docker startup can be tested using:

```bash
time docker run --rm \
  -d \
  --name startup-test \
  -p 8000:8000 \
  performance-api
```

Stop the container:

```bash
docker stop startup-test
```

Multiple repetitions should be used because startup time can vary between runs.

### Startup Results

| Environment |       Startup Time | Application Ready Time |
| ----------- | -----------------: | ---------------------: |
| VM          | Not recorded | Not recorded |
| Container   | 0.898 s | Not recorded |

---

# 18. Scalability Experiment

Scalability was evaluated by increasing the workload intensity.

## CPU Scalability

```bash
for threads in 1 2 4 8
do
  sysbench cpu \
    --cpu-max-prime=20000 \
    --threads=$threads \
    --time=30 \
    run
done
```

The results are used to study performance as the number of threads increases.

## API Scalability

```bash
wrk -t1 -c10 -d30s http://127.0.0.1:8000/health
```

```bash
wrk -t2 -c50 -d30s http://127.0.0.1:8000/health
```

```bash
wrk -t4 -c100 -d30s http://127.0.0.1:8000/health
```

```bash
wrk -t4 -c200 -d30s http://127.0.0.1:8000/health
```

The following metrics are observed:

* Throughput
* Latency
* CPU utilization
* Memory utilization
* Failed requests

---

# 19. Automated Benchmark Execution

Automation scripts were used to maintain consistent benchmark parameters.

Example CPU automation:

```bash
#!/bin/bash

OUTPUT_DIR="results/raw/cpu"
mkdir -p "$OUTPUT_DIR"

for threads in 1 2 4 8
do
    echo "Running CPU test with $threads threads"

    sysbench cpu \
      --cpu-max-prime=20000 \
      --threads=$threads \
      --time=30 \
      run > "$OUTPUT_DIR/cpu_${threads}_threads.txt"
done

echo "CPU benchmark completed."
```

The script is stored under:

```text
scripts/run_cpu.sh
```

Similar scripts can be used for:

* Memory
* Disk
* Network
* Metric collection
* Result processing
* Graph generation

Automation improves consistency and reduces manual execution errors.

---

# 20. Result Collection and Processing

Raw benchmark output is preserved without modifying the original measurements.

### Raw Results

```text
results/raw/
```

### Processed Results

```text
results/processed/
```

### Figures

```text
results/figures/
```

For example:

```text
results/processed/cpu_results.csv
```

Example CSV format:

```csv
environment,threads,execution_time,events_per_second
VM,<measured>,<measured>,<measured>
VM,<measured>,<measured>,<measured>
Container,<measured>,<measured>,<measured>
Container,<measured>,<measured>,<measured>
```

The numerical values in the final analysis are taken from the actual experimental measurements.

---

# 21. Statistical Analysis

Python and Pandas are used to process the benchmark results.

Example:

```python
import pandas as pd

df = pd.read_csv(
    "results/processed/cpu_results.csv"
)

summary = df.groupby("environment")[
    "events_per_second"
].agg([
    "mean",
    "median",
    "min",
    "max",
    "std"
])

print(summary)
```

### Statistical Measures

| Measure            | Meaning                               |
| ------------------ | ------------------------------------- |
| Mean               | Average performance                   |
| Median             | Middle value of repeated measurements |
| Minimum            | Lowest observed value                 |
| Maximum            | Highest observed value                |
| Standard Deviation | Variation between measurements        |

Repeated measurements help identify normal performance variation and unusually high or low observations.

---

# 22. Performance Difference Calculation

Different performance metrics require different comparison formulas.

## Execution Time

For execution time:

```text
Difference (%) =
((VM Time - Container Time) / VM Time) × 100
```

Python:

```python
difference = (
    (vm_time - container_time)
    / vm_time
) * 100
```

## Throughput

For throughput:

```text
Difference (%) =
((Container Throughput - VM Throughput)
 / VM Throughput) × 100
```

Python:

```python
difference = (
    (container_throughput - vm_throughput)
    / vm_throughput
) * 100
```

The formula used should always be stated with the corresponding metric.

A percentage difference should not automatically be described as "overhead" unless the calculation specifically measures overhead.

---

# 23. Results

The following sections summarize the measured experimental results.

> **Note:** The numerical values below should be populated using the actual benchmark measurements stored in `results/raw/` and `results/processed/`. No assumed benchmark values are used.

---

## 23.1 CPU Results

### CPU Performance Table

| Threads | VM Events/sec | Container Events/sec | VM Time (s) | Container Time (s) |
| ------: | ------------: | -------------------: | ----------: | -----------------: |
|       1 |        307.10 |               294.10 |     30.0013 |         30.0019 |
|       2 |        554.15 |               604.54 |     30.0029 |         30.0029 |
|       4 |        772.48 |               824.50 |     30.0035 |         30.0040 |
|       8 |        798.49 |               776.81 |     30.0069 |         30.0438 |

### CPU Statistical Summary

| Environment |    Mean | Median | Minimum | Maximum | Std. Dev. |
| ----------- | ------: | -----: | ------: | ------: | --------: |
| VM          | 608.055 | 663.315 | 307.10 | 798.49 | 228.605 |
| Container   | 624.988 | 690.675 | 294.10 | 824.50 | 239.972 |

### CPU Graph

The CPU performance graph is generated from the processed measurements.

```text
results/figures/cpu_performance.png
```

![CPU Performance](results/figures/cpu_performance.png)

### CPU Scalability Graph

```text
results/figures/cpu_scalability.png
```

![CPU Scalability](results/figures/cpu_scalability.png)

---

## 23.2 Memory Results

| Metric         |         VM | Container | Difference |
| -------------- | ---------: | --------: | ---------: |
| Operations/sec | Not recorded | Not recorded | N/A |
| Execution time | Not recorded | Not recorded | N/A |
| Latency        | Not recorded | Not recorded | N/A |

### Memory Graph

```text
results/figures/memory_performance.png
```

![Memory Performance](results/figures/memory_performance.png)

---

## 23.3 Disk Results

| Workload         |         VM | Container | Difference |
| ---------------- | ---------: | --------: | ---------: |
| Sequential Read  | 596 MiB/s | Not recorded | N/A |
| Sequential Write | 118 MiB/s | 141 MiB/s | 19.49% |
| Random Read      | 2457 IOPS | 2356 IOPS | -4.11% |
| Random Write     | 2286 IOPS | Not recorded | N/A |

### Disk Performance Graph

```text
results/figures/disk_performance.png
```

![Disk Performance](results/figures/disk_performance.png)

---

## 23.4 Network Results

| Metric          |            VM | Container | Difference |
| --------------- | ------------: | --------: | ---------: |
| Throughput      | 13.2 Gbits/sec | Not recorded | N/A |
| Retransmissions | Not recorded | Not recorded | N/A |
| Transfer        | Not recorded | Not recorded | N/A |

### Network Graph

```text
results/figures/network_performance.png
```

![Network Performance](results/figures/network_performance.png)

---

## 23.5 Application Results

### FastAPI Performance

| Metric                    |        VM | Container | Difference |
| ------------------------- | --------: | --------: | ---------: |
| Requests/sec (Health)     |    455.58 |    269.96 | -40.74% |
| Requests/sec (Compute)    |      9.58 |      6.82 | -28.81% |
| Time/request              | Not recorded | Not recorded | N/A |
| Failed Requests           | Not recorded | Not recorded | N/A |
| Latency (Health)          | 219.499 ms | 370.419 ms | 68.76% |
| Latency (Compute)         | 1044.117 ms | 1467.165 ms | 40.52% |

### Application Graph

```text
results/figures/application_performance.png
```

![Application Performance](results/figures/application_performance.png)

---

## 23.6 Startup Results

| Environment | Startup Time | Application Ready Time |
| ----------- | -----------: | ---------------------: |
| VM          | Not recorded |          Not recorded |
| Container   |     0.898 s |          Not recorded |

### Startup-Time Graph

```text
results/figures/startup_time.png
```

![Startup Time](results/figures/startup_time.png)

---

## 23.7 Scalability Results

### CPU Scalability

| Threads |     VM | Container |
| ------: | -----: | --------: |
|       1 | 307.10 |    294.10 |
|       2 | 554.15 |    604.54 |
|       4 | 772.48 |    824.50 |
|       8 | 798.49 |    776.81 |

### API Scalability

A complete workload-wise API scalability dataset was not recorded for both environments. Therefore, API scalability values are not reported here.

### Scalability Graph

A separate API scalability graph is not included because the recorded experiment data does not contain complete workload-wise VM and container measurements. The available CPU scalability measurements are represented in the CPU scalability graph above.

---

# 24. VM vs Container Comparison

The final comparison table combines the major measurements from the experiments.

| Metric             |       VM | Container | Difference |
| ------------------ | -------: | --------: | ---------: |
| CPU Performance    | 608.0550 |  624.9875 |     2.78% |
| Memory Usage       | 10240 MiB | 10240 MiB |       N/A |
| Sequential Read    | 596 MiB/s |        N/A |       N/A |
| Sequential Write   | 118 MiB/s | 141 MiB/s |    19.49% |
| Random Read        | 2457 IOPS | 2356 IOPS |    -4.11% |
| Random Write       | 2286 IOPS |        N/A |       N/A |
| Network Throughput | 13.2 Gbits/sec | N/A | N/A |
| Startup Time       | N/A | 0.898 s | N/A |
| API Requests/sec (Health) | 455.58 | 269.96 | -40.74% |
| API Requests/sec (Compute) | 9.58 | 6.82 | -28.81% |
| API Latency (Health) | 219.499 ms | 370.419 ms | 68.76% |
| API Latency (Compute) | 1044.117 ms | 1467.165 ms | 40.52% |
| Random Read        | 2457 IOPS | 2356 IOPS | -4.11% |
| Random Write       | 2286 IOPS | Not recorded | N/A |
| Network Throughput | 13.2 Gbits/sec | Not recorded | N/A |
| Startup Time       | N/A | 0.898 s | N/A |
| API Requests/sec   | 455.58 / 9.58 | 269.96 / 6.82 | -40.74% / -28.81% |
| API Latency        | 219.499 / 1044.117 ms | 370.419 / 1467.165 ms | 68.76% / 40.52% |

All measurements should be reported with appropriate units:

* CPU → events/sec
* Memory → operations/sec or latency
* Disk → MB/s and IOPS
* Network → Mbps
* Startup → seconds
* API throughput → requests/sec
* API latency → milliseconds

---

# 25. Performance Applications

The experiments represent several practical workloads used in real computing environments.

## 25.1 CPU-Intensive Applications

The Sysbench CPU workload represents applications involving substantial computational processing.

Examples include:

* Scientific computing
* Mathematical processing
* Data processing
* Batch computation
* CPU-intensive backend services

---

## 25.2 Memory-Intensive Applications

The memory benchmark represents applications that perform large numbers of memory operations.

Examples include:

* In-memory data processing
* Caching systems
* Data analytics
* Large data structures
* Memory-intensive services

---

## 25.3 Storage-Intensive Applications

The fio workload represents storage-heavy applications.

Examples include:

* Databases
* File servers
* Data pipelines
* Logging systems
* Storage services
* Large file processing

---

## 25.4 Network-Intensive Applications

The iperf3 experiment represents network-heavy workloads.

Examples include:

* Distributed applications
* Network services
* Cloud applications
* Microservices
* Data transfer systems

---

## 25.5 Application Workloads

The FastAPI application provides a practical application-level workload.

The three endpoints represent:

| Endpoint   | Workload                       |
| ---------- | ------------------------------ |
| `/health`  | Lightweight request processing |
| `/compute` | CPU-intensive processing       |
| `/memory`  | Memory-intensive processing    |

This allows the experiment to move beyond synthetic benchmarks and observe application-level behavior.

---

# 26. Discussion

The experiment evaluates VM and container environments using multiple workload categories rather than relying on a single benchmark.

The analysis considers:

* Raw benchmark measurements
* Repeated runs
* Statistical summaries
* Resource utilization
* Application-level performance
* Startup behavior
* Scalability

The results should be interpreted together with the experimental configuration.

For example, CPU results should be considered alongside:

* Number of allocated CPUs
* Number of benchmark threads
* Host workload
* VM configuration
* Container CPU limits

Similarly, disk results depend on:

* Storage device
* Virtual disk configuration
* Mounted directory
* Docker storage configuration
* fio parameters

Network results depend on:

* Network mode
* Client/server arrangement
* NAT or bridged networking
* Number of parallel streams

Therefore, the measured results represent the behavior of the specific experimental configuration used in this project.

---

# 27. Limitations

The experiment has several limitations.

1. The results depend on the hardware used for the experiment.
2. Host-system background activity can influence measurements.
3. VM performance depends on hypervisor configuration.
4. Container performance depends on Docker configuration.
5. Disk results depend on the underlying physical and virtual storage layers.
6. Network measurements depend on the selected network configuration.
7. Repeated measurements reduce random variation but cannot eliminate all environmental effects.
8. The experiments represent selected workloads and do not cover every possible application.
9. The results should not automatically be generalized to every VM or container platform.
10. Performance can change with different hardware, operating systems, hypervisors, container runtimes, resource limits, and workloads.

---

# 28. Reproducibility

The project maintains the components required to reproduce the experiments.

### Documentation

```text
docs/
```

### Benchmark Environment

```text
docker/Dockerfile
```

### Application

```text
api/main.py
api/requirements.txt
api/Dockerfile
```

### Automation

```text
scripts/
```

### Raw Results

```text
results/raw/
```

### Processed Data

```text
results/processed/
```

### Graphs

```text
results/figures/
```

The experiment should always be executed from the project root.

```bash
cd ~/5th-sem-labs/CC-Experiment-2-vm-vs-container-performance
pwd
```

The expected path is similar to:

```text
/home/<username>/5th-sem-labs/CC-Experiment-2-vm-vs-container-performance
```

---

# 29. Complete Experimental Workflow

```text
                    PROJECT START
                         |
                         v
              +---------------------+
              | Prepare Environment |
              +---------------------+
                         |
                         v
              +---------------------+
              | Configure VM        |
              +---------------------+
                         |
                         v
              +---------------------+
              | Configure Docker    |
              +---------------------+
                         |
                         v
              +---------------------+
              | Establish Baseline  |
              +---------------------+
                         |
                         v
              +---------------------+
              | CPU Benchmark       |
              +---------------------+
                         |
                         v
              +---------------------+
              | Memory Benchmark    |
              +---------------------+
                         |
                         v
              +---------------------+
              | Disk Benchmark      |
              +---------------------+
                         |
                         v
              +---------------------+
              | Network Benchmark   |
              +---------------------+
                         |
                         v
              +---------------------+
              | FastAPI Benchmark   |
              +---------------------+
                         |
                         v
              +---------------------+
              | Startup Test        |
              +---------------------+
                         |
                         v
              +---------------------+
              | Scalability Test    |
              +---------------------+
                         |
                         v
              +---------------------+
              | Collect Raw Data    |
              +---------------------+
                         |
                         v
              +---------------------+
              | Python Analysis     |
              +---------------------+
                         |
                         v
              +---------------------+
              | Graphs and Tables   |
              +---------------------+
                         |
                         v
              +---------------------+
              | Final Discussion    |
              +---------------------+
                         |
                         v
              +---------------------+
              | GitHub Repository   |
              +---------------------+
```

---

# 30. Future Work

The project can be extended in several directions.

### Kubernetes

The same workloads can be deployed using Kubernetes to study:

* Container orchestration
* Pod performance
* Replica scaling
* Resource requests and limits
* Horizontal Pod Autoscaling

### Cloud Deployment

The experiments can be repeated on cloud infrastructure using:

* Virtual machines
* Managed container services
* Kubernetes clusters

### Additional Workloads

Future experiments can include:

* Database benchmarks
* Web-server benchmarks
* Machine-learning workloads
* GPU workloads
* Distributed workloads

### Additional Metrics

Future analysis can include:

* Energy consumption
* CPU frequency
* Context switches
* Network latency distributions
* Container creation overhead
* Memory footprint
* Resource efficiency

---

# 31. Conclusion

This project provides an experimental comparison of Virtual Machines and Docker Containers using controlled workloads.

The study covers:

* CPU performance
* Memory performance
* Disk I/O
* Network performance
* FastAPI application performance
* Startup time
* Scalability
* Resource utilization
* Statistical analysis

The comparison is based on measurements collected from the actual experimental environment.

Repeated benchmark runs, raw data preservation, processed CSV files, statistical analysis, and graphical visualization provide a structured approach to evaluating the two environments.

The final conclusion is based on the **measured results obtained during the experiment**, rather than assuming beforehand that either Virtual Machines or Containers will always provide better performance.

The project demonstrates how controlled benchmarking can be used to understand the performance characteristics of different virtualization and deployment environments.

---

# 32. GitHub Workflow

The project is maintained as part of the existing Git repository.

Project location:

```text
~/5th-sem-labs/CC-Experiment-2-vm-vs-container-performance
```

The Git repository root is:

```text
~/5th-sem-labs
```

Therefore, Git operations should be performed from the repository root.

### Check Status

```bash
cd ~/5th-sem-labs
git status
```

### Add README

```bash
git add CC-Experiment-2-vm-vs-container-performance/README.md
```

### Commit

```bash
git commit -m "Update VM vs container performance README"
```

### Push

```bash
git push origin main
```

Future experiment updates can use meaningful commits such as:

```bash
git commit -m "Add CPU benchmark results"
```

```bash
git commit -m "Add memory benchmark"
```

```bash
git commit -m "Add disk I/O benchmark"
```

```bash
git commit -m "Add network benchmark"
```

```bash
git commit -m "Add FastAPI workload"
```

```bash
git commit -m "Add performance analysis"
```

```bash
git commit -m "Add benchmark graphs"
```

```bash
git commit -m "Update README"
```

Only required project files should be committed.

VM disk files, credentials, passwords, API keys, and unnecessary temporary files should not be uploaded.

---

# 33. Author

## Krupa Akki

**CSE (Artificial Intelligence) Student**

GitHub: [Krupa1310](https://github.com/Krupa1310)

### Project

**Performance Analysis of Virtual Machines and Containers**

This project demonstrates practical benchmarking, virtualization, containerization, performance analysis, data processing, and reproducible experimentation.

---

## Project Highlights

* Virtual Machine performance analysis
* Docker container performance analysis
* Sysbench CPU benchmarking
* Sysbench memory benchmarking
* fio disk benchmarking
* iperf3 network benchmarking
* FastAPI application benchmarking
* Startup-time analysis
* Scalability testing
* Automated benchmark execution
* CSV-based data processing
* Statistical analysis using Python
* Graph generation using Matplotlib
* Reproducible GitHub-based project organization

---

## Repository Organization

| Directory            | Purpose                                    |
| -------------------- | ------------------------------------------ |
| `docs/`              | Configuration and experiment documentation |
| `docker/`            | General benchmark Docker environment       |
| `api/`               | FastAPI application                        |
| `scripts/`           | Automation and analysis scripts            |
| `workloads/`         | Workload organization                      |
| `results/raw/`       | Original benchmark outputs                 |
| `results/processed/` | Processed CSV data                         |
| `results/figures/`   | Generated graphs                           |
| `analysis/`          | Notebook-based analysis                    |

---

## Final Note

All numerical results, graphs, statistical values, and comparison values in this project are based on the actual experimental measurements collected during execution.

The project is designed so that another user can inspect the configuration, reproduce the workloads, process the measurements, and understand how the final comparison was obtained.
