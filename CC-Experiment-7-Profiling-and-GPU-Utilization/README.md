# PGC-Experiment-7-Profiling-and-GPU-Utilization

**Course:** Cloud Computing / GPU Programming Lab  
**Experiment:** Profiling and GPU Utilization

## 1. Aim

Profile a GPU workload to identify where execution time is lost, then improve GPU utilization by overlapping host-to-device data transfer with computation.

## 2. Learning Outcomes

- Capture a GPU execution timeline and identify idle gaps and host-device transfers.
- Classify kernels as compute-bound or memory-bound using arithmetic intensity.
- Use pinned host memory and two CUDA streams to overlap data transfer and computation.
- Compare GPU utilization and execution time between baseline and optimized implementations.

## 3. Files

| File | Description |
|---|---|
| `gpu_workload.py` | Runs the baseline and optimized GPU workloads and optionally exports profiler traces. |
| `analyze_trace.py` | Reads PyTorch Chrome trace JSON files and reports kernel activity, copy activity, overlap, and idle gaps. |

## 4. Requirements

- NVIDIA GPU and a compatible NVIDIA driver
- Python 3.9 or later
- PyTorch built with CUDA support
- Approximately 2 GB of free GPU memory for the default workload
- `nvidia-smi` (for GPU utilization logging)

Install a CUDA-enabled PyTorch build using the command appropriate for your system. The lab manual gives this example:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Check CUDA availability:

```bash
nvidia-smi
python --version
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CUDA unavailable')"
```

The CUDA check should report `True` and the GPU name before running the workload.

## 5. Procedure

### Step 1: Run and profile the baseline

In a second terminal, start GPU utilization logging:

```bash
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -lms 100 > smi_baseline.csv
```

Run the baseline workload:

```bash
python gpu_workload.py --mode baseline --profile
```

Stop the utilization logger with `Ctrl+C` after the workload finishes. The run creates `trace_baseline.json`.

### Step 2: Analyze the baseline trace

Open `trace_baseline.json` in [Perfetto](https://ui.perfetto.dev/) or Chrome tracing to inspect GPU copy and kernel activity.

Run:

```bash
python analyze_trace.py trace_baseline.json
```

Record the profiled window, kernel busy time, estimated GPU utilization, copy activity, and idle gaps.

### Step 3: Classify the kernels

Arithmetic intensity is:

\[
AI = \frac{\text{FLOPs performed}}{\text{bytes transferred from GPU memory}}
\]

Compare arithmetic intensity with the GPU ridge point:

\[
\text{Ridge point} = \frac{\text{Peak FP32 FLOP/s}}{\text{Peak memory bandwidth in GB/s}}
\]

An arithmetic intensity above the ridge point suggests a compute-bound kernel; below it suggests a memory-bound kernel.

For the workload in this experiment, the lab manual gives these approximate classifications:

| Kernel | Arithmetic intensity | Expected classification |
|---|---:|---|
| GEMM | 249 FLOP/byte | Compute-bound |
| ReLU / multiply / add | 0.125 FLOP/byte | Memory-bound |
| Sum reduction | 0.25 FLOP/byte | Memory-bound |

These are reference calculations; use the specifications of the GPU being tested for its ridge point.

### Step 4: Run the optimized version

Start a separate utilization log:

```bash
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -lms 100 > smi_optimized.csv
```

Run:

```bash
python gpu_workload.py --mode optimized --profile
```

Stop the logger with `Ctrl+C`. The run creates `trace_optimized.json`.

The optimized implementation uses pinned host memory, a copy stream, a compute stream, two device buffers, and CUDA events to coordinate buffer reuse.

### Step 5: Compare both traces

```bash
python analyze_trace.py trace_baseline.json trace_optimized.json
```

Compare the baseline and optimized execution time, utilization, idle gaps, and copy/kernel overlap. The checksums from the two workload modes should match, allowing for tiny floating-point differences.

## 6. Output Files

The commands above generate the following files when the experiment is actually run:

- `trace_baseline.json`
- `trace_optimized.json`
- `smi_baseline.csv`
- `smi_optimized.csv`

Capture screenshots of the baseline and optimized timelines from Perfetto for the lab report. Do not report sample values as measured results; record the values from the actual GPU used.

## 7. Reference Results from the Lab Manual

The manual provides the following **worked sample values** for a mid-range GPU. Actual results vary by GPU, driver, and system configuration.

| Metric | Baseline (sample) | Optimized (sample) |
|---|---:|---:|
| Total time | 4.76 s | 2.62 s |
| Time per batch | 23.8 ms | 13.1 ms |
| Throughput | 42 batches/s | 76 batches/s |
| GPU utilization (nvidia-smi average) | approx. 55% | approx. 96% |
| Kernel busy / profiled window | 52% | 94% |
| Idle gaps over 50 microseconds | 9 | 0 |
| Copy time overlapped with kernels | 0 ms | approx. 50 ms |

**Important:** These are manual reference values, not results measured on this laptop.

## 8. Conclusion

The baseline workload performs data transfers and computation sequentially, which can leave the GPU compute units idle while data is being copied. The optimized implementation uses pinned host memory and two CUDA streams with double buffering to overlap the transfer of the next batch with computation on the current batch. The profiler traces and timing measurements are used to evaluate whether this reduces idle time and improves GPU utilization on the tested system.
