# Hypervisor Performance Analysis

## Objective

To analyze and compare the CPU performance of virtual machines running on a Type-1 hypervisor and a Type-2 hypervisor.

## Hypervisors

* **Type-1:** Proxmox VE
* **Type-2:** VMware Workstation

## Virtual Machine Configuration

| Resource  | Configuration |
| --------- | ------------- |
| Guest OS  | Ubuntu        |
| CPU       | 2 vCPU        |
| Memory    | 2 GB RAM      |
| Disk      | 20 GB         |
| Benchmark | Sysbench      |

## Type-1 Hypervisor – Proxmox VE

A Type-1 hypervisor runs directly on the physical hardware. It does not require a general-purpose host operating system underneath it.

### Working

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

### Configuration

* Hypervisor: Proxmox VE
* Guest OS: Ubuntu
* CPU: 2 vCPU
* Memory: 2 GB RAM
* Disk: 20 GB
* Benchmark: Sysbench CPU

## Type-2 Hypervisor – VMware Workstation

A Type-2 hypervisor runs as an application on top of a host operating system.

### Working

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

### Configuration

* Hypervisor: VMware Workstation
* Host OS: Windows
* Guest OS: Ubuntu
* CPU: 2 vCPU
* Memory: 2 GB RAM
* Disk: 20 GB
* Network: NAT
* Benchmark: Sysbench CPU

## Hypervisor Comparison

| Feature                  | Type-1: Proxmox VE | Type-2: VMware Workstation |
| ------------------------ | ------------------ | -------------------------- |
| Hypervisor type          | Type-1             | Type-2                     |
| Runs on                  | Physical hardware  | Host operating system      |
| Host OS below hypervisor | Not required       | Required                   |
| Guest OS                 | Ubuntu             | Ubuntu                     |
| CPU                      | 2 vCPU             | 2 vCPU                     |
| Memory                   | 2 GB RAM           | 2 GB RAM                   |
| Disk                     | 20 GB              | 20 GB                      |
| Benchmark                | Sysbench CPU       | Sysbench CPU               |

The same VM configuration and CPU benchmark are used for both hypervisor types so that their measured performance can be documented consistently.

## CPU Benchmark

The following Sysbench command is used inside the respective Ubuntu virtual machine:

```bash
sysbench cpu --cpu-max-prime=20000 run
```

The benchmark results include execution time, total events, events per second, and latency.

## Results

The actual benchmark results for Type-1 and Type-2 hypervisors are recorded after running the experiments.

### Type-1 – Proxmox VE

The Sysbench results obtained from the Ubuntu VM running on Proxmox VE are recorded in the Type-1 results section.

### Type-2 – VMware Workstation

The Sysbench results obtained from the Ubuntu VM running on VMware Workstation are recorded in the Type-2 results section.

## Conclusion

The experiment provides a practical comparison of CPU performance when running an Ubuntu virtual machine using a Type-1 hypervisor and a Type-2 hypervisor under the same VM resource configuration.

