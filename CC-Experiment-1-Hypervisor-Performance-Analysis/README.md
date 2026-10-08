# ☁️ CC Experiment 01 - Hypervisor Analysis

## 📑 Table of Contents

* [1. Problem Statement](#1-problem-statement)
* [2. Objectives](#2-objectives)
* [3. Type-1 Hypervisor - Proxmox VE](#3-type-1-hypervisor---proxmox-ve)

  * [3.1 Configuration](#31-configuration)
  * [3.2 Architecture](#32-architecture)
  * [3.3 Execution Steps](#33-execution-steps)
  * [3.4 Results](#34-results)
* [4. Type-2 Hypervisor - VMware Workstation](#4-type-2-hypervisor---vmware-workstation)

  * [4.1 Configuration](#41-configuration)
  * [4.2 Architecture](#42-architecture)
  * [4.3 Execution Steps](#43-execution-steps)
  * [4.4 Results](#44-results)
* [5. VM vs Container Performance Concept](#5-vm-vs-container-performance-concept)

  * [Virtual Machine](#virtual-machine)
  * [Container](#container)
  * [VM vs Container](#vm-vs-container)
* [6. Type-1 vs Type-2 Comparison Table](#6-type-1-vs-type-2-comparison-table)

  * [Performance Comparison](#performance-comparison)
* [7. Performance Comparison Graph](#7-performance-comparison-graph)

  * [Performance Comparison Graph Data](#performance-comparison-graph-data)
  * [Graph](#graph)
* [8. Results and Graph Files](#8-results-and-graph-files)
* [9. Conclusion](#9-conclusion)
* [10. Author](#10-author)

---

## 1. Problem Statement

Virtual machines can be deployed using different types of hypervisors. A **Type-1 hypervisor** runs directly on physical hardware, while a **Type-2 hypervisor** runs on top of a host operating system.

This experiment analyzes the CPU performance of an Ubuntu virtual machine running on a Type-1 hypervisor and a Type-2 hypervisor using the same virtual machine configuration and the same CPU benchmark.

The measured results are recorded and compared to understand the performance characteristics of both hypervisor types.

---

## 2. Objectives

* To understand the concept of virtualization and hypervisors.
* To understand the difference between Type-1 and Type-2 hypervisors.
* To configure an Ubuntu virtual machine on Proxmox VE.
* To configure an Ubuntu virtual machine on VMware Workstation.
* To execute a CPU benchmark using Sysbench.
* To record CPU performance metrics from both environments.
* To compare the measured performance of Type-1 and Type-2 hypervisors.
* To understand the basic performance difference between virtual machines and containers.

---

# 3. Type-1 Hypervisor - Proxmox VE

## 3.1 Configuration

| Resource        | Configuration            |
| --------------- | ------------------------ |
| Hypervisor      | Proxmox VE               |
| Hypervisor Type | Type-1                   |
| Guest OS        | Ubuntu                   |
| CPU             | 2 vCPU                   |
| Memory          | 2 GB RAM                 |
| Disk            | 20 GB                    |
| Network         | As configured in Proxmox |
| Benchmark       | Sysbench CPU             |

### Configuration Description

Proxmox VE is used as the Type-1 hypervisor. The Ubuntu virtual machine is configured with 2 vCPU, 2 GB RAM, and a 20 GB virtual disk.

The same basic VM resource configuration is used for the Type-2 experiment to maintain consistent experimental conditions.

---

## 3.2 Architecture

```text
Physical Hardware
       ↓
   Proxmox VE
       ↓
 Ubuntu Virtual Machine
       ↓
 Sysbench CPU Benchmark
       ↓
 Performance Result
```

Proxmox VE runs directly on the physical hardware and manages the Ubuntu virtual machine.

---

## 3.3 Execution Steps

### Step 1: Install and Start Proxmox VE

Proxmox VE is installed and configured as the Type-1 hypervisor.

### Step 2: Create the Ubuntu Virtual Machine

An Ubuntu VM is created in Proxmox VE.

### Step 3: Configure VM Resources

The VM is configured with:

* 2 vCPU
* 2 GB RAM
* 20 GB disk

### Step 4: Start the Virtual Machine

The Ubuntu VM is started from the Proxmox interface.

### Step 5: Open the Ubuntu Terminal

The Ubuntu terminal is accessed inside the virtual machine.

### Step 6: Install Sysbench

```bash
sudo apt update
sudo apt install sysbench -y
```

### Step 7: Verify Sysbench

```bash
sysbench --version
```

### Step 8: Run CPU Benchmark

```bash
sysbench cpu --cpu-max-prime=20000 run
```

### Step 9: Record the Result

The following Sysbench metrics are recorded:

* Total time
* Total events
* Events per second
* Average latency
* Maximum latency

---

## 3.4 Results

The Proxmox benchmark measurements are currently unavailable.

| Metric                  |      Proxmox VE |
| ----------------------- | --------------: |
| Total Time              | **TO BE ADDED** |
| Total Events            | **TO BE ADDED** |
| Events Per Second       | **TO BE ADDED** |
| Average Latency         | **TO BE ADDED** |
| Maximum Latency         | **TO BE ADDED** |
| 95th Percentile Latency | **TO BE ADDED** |

> ⚠️ No numerical performance values are assumed for Proxmox.

---

# 4. Type-2 Hypervisor - VMware Workstation

## 4.1 Configuration

| Resource        | Configuration      |
| --------------- | ------------------ |
| Hypervisor      | VMware Workstation |
| Hypervisor Type | Type-2             |
| Host OS         | Windows            |
| Guest OS        | Ubuntu             |
| CPU             | 2 vCPU             |
| Memory          | 2 GB RAM           |
| Disk            | 20 GB              |
| Network         | NAT                |
| Benchmark       | Sysbench CPU       |

### Configuration Description

VMware Workstation is used as the Type-2 hypervisor. It runs as an application on the Windows host operating system and manages the Ubuntu virtual machine.

The VM is configured with the same CPU, memory, and disk resources used for the Proxmox experiment.

---

## 4.2 Architecture

```text
Physical Hardware
       ↓
    Windows OS
       ↓
VMware Workstation
       ↓
 Ubuntu Virtual Machine
       ↓
 Sysbench CPU Benchmark
       ↓
 Performance Result
```

VMware Workstation runs on top of the Windows host operating system and provides the virtual environment for Ubuntu.

---

## 4.3 Execution Steps

### Step 1: Install VMware Workstation

VMware Workstation is installed on the Windows host operating system.

### Step 2: Create the Ubuntu Virtual Machine

An Ubuntu VM is created using VMware Workstation.

### Step 3: Configure VM Resources

The VM is configured with:

* 2 vCPU
* 2 GB RAM
* 20 GB disk
* NAT networking

### Step 4: Start the Virtual Machine

The Ubuntu VM is started using VMware Workstation.

### Step 5: Open the Ubuntu Terminal

The Ubuntu terminal is accessed inside the virtual machine.

### Step 6: Install Sysbench

```bash
sudo apt update
sudo apt install sysbench -y
```

### Step 7: Verify Sysbench

```bash
sysbench --version
```

### Step 8: Run CPU Benchmark

```bash
sysbench cpu --cpu-max-prime=20000 run
```

### Step 9: Record the Result

The following Sysbench metrics are recorded:

* Total time
* Total events
* Events per second
* Average latency
* Maximum latency

---

## 4.4 Results

The actual Sysbench results obtained from the VMware Ubuntu VM are recorded below.

| Metric                  | VMware Workstation |
| ----------------------- | -----------------: |
| Sysbench Version        |             1.0.20 |
| Benchmark               |                CPU |
| Prime Numbers Limit     |             20,000 |
| Threads                 |                  1 |
| Total Time              |      **10.0006 s** |
| Total Events            |         **24,366** |
| Events Per Second       |       **2,436.05** |
| Minimum Latency         |        **0.40 ms** |
| Average Latency         |        **0.41 ms** |
| Maximum Latency         |        **4.39 ms** |
| 95th Percentile Latency |        **0.42 ms** |
| Latency Sum             |     **9992.75 ms** |

### Observation

The CPU benchmark completed in approximately **10 seconds**. The VM processed **24,366 total events** and achieved a throughput of **2,436.05 events per second**.

The measured average latency was **0.41 ms**. The minimum latency was **0.40 ms**, while the maximum observed latency was **4.39 ms**. The 95th percentile latency was **0.42 ms**.

---

# 5. VM vs Container Performance Concept

## Virtual Machine

A virtual machine provides a complete virtualized environment including a guest operating system.

```text
Physical Hardware
       ↓
Hypervisor
       ↓
Guest Operating System
       ↓
Application
```

Each VM has its own guest operating system and virtual hardware resources.

## Container

Containers share the host operating system kernel while isolating applications and their dependencies.

```text
Physical Hardware
       ↓
Host Operating System
       ↓
Container Runtime
       ↓
Container
       ↓
Application
```

## VM vs Container

| Feature           | Virtual Machine                      | Container                          |
| ----------------- | ------------------------------------ | ---------------------------------- |
| Operating System  | Separate guest OS                    | Shares host OS kernel              |
| Virtualization    | Hardware-level virtualization        | OS-level virtualization            |
| Startup           | Generally slower                     | Generally faster                   |
| Resource Overhead | Higher                               | Lower                              |
| Isolation         | Strong isolation through VM boundary | Process-level isolation            |
| Typical Use       | Full OS environments                 | Lightweight application deployment |

The VM experiment in this project focuses on hypervisor-based virtualization. Container performance is considered as a related virtualization concept for comparison and understanding.

---

# 6. Type-1 vs Type-2 Comparison Table

| Feature                           | Type-1: Proxmox VE            | Type-2: VMware Workstation |
| --------------------------------- | ----------------------------- | -------------------------- |
| Hypervisor Type                   | Type-1                        | Type-2                     |
| Runs On                           | Physical hardware             | Host operating system      |
| Host OS Required Below Hypervisor | No                            | Yes                        |
| Host OS                           | Not required below hypervisor | Windows                    |
| Guest OS                          | Ubuntu                        | Ubuntu                     |
| CPU                               | 2 vCPU                        | 2 vCPU                     |
| Memory                            | 2 GB RAM                      | 2 GB RAM                   |
| Disk                              | 20 GB                         | 20 GB                      |
| Benchmark                         | Sysbench CPU                  | Sysbench CPU               |
| Virtualization Layer              | Directly on hardware          | Above host OS              |

## Performance Comparison

| Metric                  |      Proxmox VE | VMware Workstation |
| ----------------------- | --------------: | -----------------: |
| Total Execution Time    | **TO BE ADDED** |      **10.0006 s** |
| Total Events            | **TO BE ADDED** |         **24,366** |
| Events Per Second       | **TO BE ADDED** |       **2,436.05** |
| Average Latency         | **TO BE ADDED** |        **0.41 ms** |
| Maximum Latency         | **TO BE ADDED** |        **4.39 ms** |
| 95th Percentile Latency | **TO BE ADDED** |        **0.42 ms** |

> ⚠️ Proxmox performance values are not included because the corresponding benchmark output is unavailable.

---

# 7. Performance Comparison Graph

The performance graph is intended to compare the **actual Sysbench results** obtained from the Type-1 and Type-2 experiments.

The following metrics are compared:

* Total Execution Time
* Events Per Second
* Average Latency
* Maximum Latency

## Performance Comparison Graph Data

| Metric                  |      Proxmox VE | VMware Workstation |
| ----------------------- | --------------: | -----------------: |
| Total Execution Time    | **TO BE ADDED** |      **10.0006 s** |
| Events Per Second       | **TO BE ADDED** |       **2,436.05** |
| Average Latency         | **TO BE ADDED** |        **0.41 ms** |
| Maximum Latency         | **TO BE ADDED** |        **4.39 ms** |
| 95th Percentile Latency | **TO BE ADDED** |        **0.42 ms** |

## Graph

The final comparison graph will be generated using the actual benchmark values from both environments.

```text
Performance Comparison

        Proxmox VE        VMware Workstation
              │                    │
              │                    │
              │                    │
              │                    │
              └────────────────────┘

       Actual Sysbench values will be plotted
```

> ⚠️ The graph must be generated from the **actual Sysbench output**. No Proxmox benchmark values are assumed or manually created.

---

# 8. Results and Graph Files

The project can contain the following files:

```text
CC-Experiment-01-Hypervisor-Analysis/
│
├── screenshots/
│   ├── type1-proxmox/
│   ├── type2-vmware/
│   └── comparison/
│
├── results/
│   ├── performance-analysis.md
│   └── hypervisor-performance-comparison.png
│
└── README.md
```

The file:

```text
results/hypervisor-performance-comparison.png
```

will contain the final performance comparison graph.

---

# 9. Conclusion

The experiment demonstrates the working and configuration of Type-1 and Type-2 hypervisors using Proxmox VE and VMware Workstation respectively.

An Ubuntu virtual machine is configured in both environments with the same basic resources, and Sysbench is used to measure CPU performance.

The VMware Workstation experiment produced **10.0006 seconds** of execution time, **24,366 total events**, **2,436.05 events per second**, and an **average latency of 0.41 ms**.

The Proxmox performance values are currently unavailable, so no numerical performance comparison is made for Proxmox at this stage.

The experiment also introduces the difference between virtual machines and containers in terms of operating system usage, virtualization approach, resource overhead, and application isolation.

---

# 10. Author

**Krupa Akki**

CSE (Artificial Intelligence)

K.L.E. Technological University
