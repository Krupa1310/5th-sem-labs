# Experiment 2: Performance Analysis of Virtual Machines and Containers

## 📑 Table of Contents

- [1. Problem Statement](#1-problem-statement)
- [2. Objectives](#2-objectives)
- [3. Introduction](#3-introduction)
- [4. Technologies Used](#4-technologies-used)
- [5. System Requirements](#5-system-requirements)
- [6. Architecture](#6-architecture)
- [7. Implementation](#7-implementation)
- [8. Experimental Procedure](#8-experimental-procedure)
- [9. Performance Analysis](#9-performance-analysis)
- [10. Results](#10-results)
- [11. Advantages](#11-advantages)
- [12. Conclusion](#12-conclusion)

---

## 1. Problem Statement

Virtual Machines and Containers are two important technologies used in cloud computing for resource sharing and application deployment. However, they differ in terms of architecture, resource utilization, startup time, and performance.

The aim of this experiment is to understand and compare the performance of Virtual Machines and Containers based on their resource usage, execution, and operational characteristics.

## 2. Objectives

- To understand virtualization and containerization.
- To study the working of Virtual Machines and Containers.
- To configure and run a Virtual Machine.
- To create and run Docker containers.
- To compare resource utilization and performance.
- To understand the advantages and limitations of both technologies.

## 3. Introduction

Virtualization allows multiple operating systems to run on a single physical machine using a hypervisor.

A Virtual Machine provides a complete virtualized hardware environment and runs its own guest operating system.

Containerization allows applications to run in isolated environments while sharing the host operating system kernel.

Docker is a popular platform used to create and manage containers.

This experiment focuses on understanding the differences between Virtual Machines and Containers through practical execution and performance analysis.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| VMware Workstation | Virtual Machine creation |
| Ubuntu | Guest Operating System |
| Docker Desktop | Container management |
| Docker | Containerization |
| Windows | Host Operating System |
| PowerShell | Command execution |
| Task Manager | Resource monitoring |

## 5. System Requirements

| Component | Configuration |
|---|---|
| Host OS | Windows |
| Virtualization Software | VMware Workstation |
| Guest OS | Ubuntu |
| Container Platform | Docker Desktop |
| Processor | Intel/AMD processor |
| RAM | Depends on available system resources |
| Storage | Sufficient free disk space |

## 6. Architecture

### Virtual Machine Architecture

```text
       Physical Hardware
               |
               v
           Hypervisor
               |
               v
        Virtual Hardware
               |
               v
        Guest Operating System
               |
               v
           Applications
```

### Container Architecture

```text
       Physical Hardware
               |
               v
        Host Operating System
               |
               v
          Docker Engine
               |
        +------+------+
        |             |
        v             v
    Container 1   Container 2
        |             |
        v             v
    Application   Application
```

## 7. Implementation

The experiment involves setting up a Virtual Machine using VMware Workstation and creating containers using Docker.

The following activities are performed:

- Installation and configuration of VMware Workstation.
- Creation of an Ubuntu Virtual Machine.
- Installation and configuration of Docker Desktop.
- Execution of Docker containers.
- Monitoring resource utilization.
- Comparing Virtual Machines and Containers.

## 8. Experimental Procedure

### Step 1: Virtual Machine Setup

1. Open VMware Workstation.
2. Select Create a New Virtual Machine.
3. Choose the Ubuntu ISO file.
4. Configure processor, memory, and storage.
5. Complete the virtual machine setup.
6. Start the virtual machine and install Ubuntu.

### Step 2: Verify Virtual Machine

Start the Ubuntu Virtual Machine and verify that the guest operating system is working correctly.

### Step 3: Docker Setup

1. Install Docker Desktop.
2. Start Docker Desktop.
3. Open PowerShell.
4. Verify Docker installation.

```powershell
docker --version
```

### Step 4: Run Docker Container

Execute the following command:

```powershell
docker run hello-world
```

This verifies that Docker is installed and working correctly.

### Step 5: Monitor Resource Utilization

Use Windows Task Manager and Docker commands to observe resource utilization.

```powershell
docker stats
```

This command displays the CPU, memory, and network usage of running containers.

## 9. Performance Analysis

The performance of Virtual Machines and Containers can be compared using the following parameters:

| Parameter | Virtual Machine | Container |
|---|---|---|
| Architecture | Includes guest OS | Shares host OS kernel |
| Startup Time | Generally slower | Generally faster |
| Resource Usage | Higher overhead | Lower overhead |
| Isolation | Hardware-level virtualization | OS-level isolation |
| Portability | Depends on VM configuration | Easily portable |
| Storage | Usually requires more storage | Usually requires less storage |

## 10. Results

The experiment was performed successfully by setting up a Virtual Machine and executing Docker containers.

The following observations were made:

- A Virtual Machine was created using VMware Workstation.
- Ubuntu was installed as the guest operating system.
- Docker Desktop was installed and configured.
- Docker container execution was verified using the hello-world image.
- Resource utilization was observed using monitoring tools.
- Virtual Machines and Containers were compared based on their architecture and resource requirements.

### Result Screenshots

Add your experiment screenshots below:

```text
screenshots/
```

## 11. Advantages

- Helps understand virtualization and containerization.
- Demonstrates resource sharing.
- Provides practical experience with VMware and Docker.
- Helps compare different deployment technologies.
- Explains resource utilization and isolation.

## 12. Conclusion

In this experiment, Virtual Machines and Containers were studied and executed using VMware Workstation and Docker.

An Ubuntu Virtual Machine was configured, and Docker containers were successfully executed.

The experiment helped understand the architectural differences, resource utilization, isolation, and performance characteristics of Virtual Machines and Containers.

Thus, the experiment demonstrates the importance of virtualization and containerization in cloud computing.

---

**Author:** Krupa Akki  
**Course:** Cloud Computing  
**Experiment:** 2
