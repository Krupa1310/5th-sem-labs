# Hypervisor Performance Analysis

## Objective

To analyze and compare the CPU performance of virtual machines running on a Type-1 hypervisor and a Type-2 hypervisor.

## Hypervisors

- **Type-1:** Proxmox VE
- **Type-2:** VMware Workstation

## Virtual Machine Configuration

| Resource | Configuration |
|---|---|
| Guest OS | Ubuntu |
| CPU | 2 vCPU |
| Memory | 2 GB RAM |
| Disk | 20 GB |
| Benchmark | Sysbench |

## CPU Benchmark

```bash
sysbench cpu --cpu-max-prime=20000 run
```
