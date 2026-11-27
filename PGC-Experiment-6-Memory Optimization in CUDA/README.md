# PGC-Experiment-6-Memory-Optimization-in-CUDA

## Table of Contents

1. [Aim](#1-aim)
2. [Learning Outcomes](#2-learning-outcomes)
3. [Theory](#3-theory)
   - [3.1 Memory Coalescing](#31-memory-coalescing)
   - [3.2 Matrix Transpose](#32-matrix-transpose)
   - [3.3 Naive Matrix Multiplication](#33-naive-matrix-multiplication)
   - [3.4 Performance Calculations](#34-performance-calculations)
4. [Requirements](#4-requirements)
5. [Program Structure](#5-program-structure)
6. [CUDA Kernel Implementation](#6-cuda-kernel-implementation)
   - [6.1 Constants](#61-constants)
   - [6.2 Uncoalesced Transpose Kernel](#62-uncoalesced-transpose-kernel)
   - [6.3 Coalesced Transpose Kernel](#63-coalesced-transpose-kernel)
   - [6.4 Naive Matrix Multiplication Kernel](#64-naive-matrix-multiplication-kernel)
   - [6.5 Timing and Verification](#65-timing-and-verification)
7. [Compilation and Execution](#7-compilation-and-execution)
8. [Expected Output](#8-expected-output)
9. [Observation Table](#9-observation-table)
10. [Analysis and Discussion](#10-analysis-and-discussion)
11. [Troubleshooting](#11-troubleshooting)
12. [Conclusion](#12-conclusion)
---

## 1. Aim

To study how global-memory access patterns affect CUDA kernel performance by comparing uncoalesced and coalesced matrix transpose operations, executing naive matrix multiplication, and measuring their GPU execution times.

## 2. Learning Outcomes

After completing this experiment, we should be able to:

- Explain memory coalescing and its importance for global-memory bandwidth.
- Write and launch two-dimensional CUDA kernels using `dim3` grids and blocks.
- Use shared memory to convert strided global-memory access into coalesced access.
- Measure kernel execution time using CUDA events.
- Calculate effective memory bandwidth in GB/s and floating-point performance in GFLOPS.
- Verify GPU results against CPU reference calculations.

## 3. Theory

### 3.1 Memory Coalescing

A GPU executes threads in groups of 32 called **warps**. When threads in a warp access neighbouring global-memory addresses, the hardware combines these accesses into a small number of memory transactions. This is called **memory coalescing**.

When threads access scattered addresses or addresses separated by a large stride, more memory transactions are required. This reduces effective memory bandwidth.

| Feature | Coalesced Access | Uncoalesced Access |
|---|---|---|
| Thread access pattern | Consecutive addresses | Strided or scattered addresses |
| Memory transactions | Few transactions | More transactions |
| Bandwidth utilization | High | Low |
| Performance | Faster | Slower |

For a warp of 32 threads:

- Coalesced access: thread `i` accesses `base + i`.
- Uncoalesced access: thread `i` accesses `base + i × N`.

### 3.2 Matrix Transpose

Matrix transpose changes the rows of a matrix into columns.

For an input matrix `in`, the transpose operation is:

```text
out[j][i] = in[i][j]
```

For a row-major matrix of size `N × N`, the element at row `r` and column `c` is stored at:

```text
index = r * N + c
```

**Uncoalesced transpose**

- Each CUDA thread copies one matrix element.
- Consecutive threads read consecutive elements from a row.
- The output writes are separated by a stride of `N`.
- These strided writes require more global-memory transactions.

**Coalesced transpose**

- A block loads a `32 × 32` tile into shared memory.
- Threads first perform coalesced global-memory reads.
- `__syncthreads()` ensures that the tile is fully loaded.
- The tile is written in transposed order using coalesced global-memory writes.
- The shared-memory array is declared as `tile[32][33]`. The extra column helps avoid shared-memory bank conflicts.

### 3.3 Naive Matrix Multiplication

Matrix multiplication calculates:

```text
C = A × B
```

For three `N × N` matrices:

```text
C[i][j] = sum(A[i][k] * B[k][j])
```

In the naive CUDA implementation:

- One thread calculates one output element `C[row][col]`.
- Each thread executes a loop of `N` iterations.
- Every iteration reads one element from matrix `A` and one from matrix `B`.
- The same input values may be fetched repeatedly from global memory.
- Shared-memory data reuse is not implemented, so the kernel is a baseline implementation that can be optimized further.

### 3.4 Performance Calculations

| Metric | Formula |
|---|---|
| Effective transpose bandwidth | `(2 × N × N × 4 bytes) / time` |
| Matrix multiplication operations | `2 × N³` floating-point operations |
| Matrix multiplication performance | `(2 × N³) / time` |
| Transpose speedup | `Uncoalesced time / Coalesced time` |

Time must be converted to seconds when calculating bandwidth and GFLOPS. The program uses CUDA events to measure GPU execution time.

## 4. Requirements

### Hardware

- Computer or lab machine with an NVIDIA GPU.
- Sufficient GPU memory for the selected matrix sizes.

### Software

- NVIDIA GPU driver.
- NVIDIA CUDA Toolkit.
- CUDA C/C++ compiler (`nvcc`).
- C/C++ development environment.
- Alternatively, Google Colab with a GPU runtime.

### Verify the Environment

Check the NVIDIA GPU and driver:

```bash
nvidia-smi
```

Check the CUDA compiler:

```bash
nvcc --version
```

For Google Colab:

1. Open Google Colab.
2. Select **Runtime → Change runtime type**.
3. Choose **GPU** as the hardware accelerator.
4. Run `!nvidia-smi` to verify GPU availability.

## 5. Program Structure

The experiment uses one CUDA source file named `exp6.cu`.

```text
PGC-Experiment-6-Memory-Optimization-in-CUDA/
│
├── README.md
├── exp6.cu
└── screenshots/
    └── (execution screenshots)
```

The CUDA program contains the following parts:

| Part | Description |
|---|---|
| Part 1 | Header files, constants and CUDA error-checking macro |
| Part 2 | Uncoalesced and coalesced matrix transpose kernels |
| Part 3 | Naive matrix multiplication kernel |
| Part 4 | CUDA event timing and result-verification functions |
| Part 5 | Host code for memory allocation, kernel launches and result display |

## 6. CUDA Kernel Implementation

### 6.1 Constants

```cpp
#define TILE 32
#define BLK 16
```

- `TILE = 32` defines the transpose tile and block dimensions.
- `BLK = 16` defines the matrix multiplication block dimensions.

### 6.2 Uncoalesced Transpose Kernel

The uncoalesced kernel reads input elements row-wise but writes output elements with a stride of `N`.

```cpp
__global__ void transposeNaive(const float *in, float *out, int N)
{
    int x = blockIdx.x * TILE + threadIdx.x;
    int y = blockIdx.y * TILE + threadIdx.y;

    if (x < N && y < N)
        out[x * N + y] = in[y * N + x];
}
```

### 6.3 Coalesced Transpose Kernel

The coalesced kernel uses shared memory to perform the transpose while maintaining coalesced global-memory accesses.

```cpp
__global__ void transposeCoalesced(const float *in, float *out, int N)
{
    __shared__ float tile[TILE][TILE + 1];

    int x = blockIdx.x * TILE + threadIdx.x;
    int y = blockIdx.y * TILE + threadIdx.y;

    if (x < N && y < N)
        tile[threadIdx.y][threadIdx.x] = in[y * N + x];

    __syncthreads();

    x = blockIdx.y * TILE + threadIdx.x;
    y = blockIdx.x * TILE + threadIdx.y;

    if (x < N && y < N)
        out[y * N + x] = tile[threadIdx.x][threadIdx.y];
}
```

### 6.4 Naive Matrix Multiplication Kernel

Each thread computes one element of the output matrix by accumulating the products of the corresponding row of `A` and column of `B`.

```cpp
__global__ void matMulNaive(const float *A, const float *B,
                            float *C, int N)
{
    int row = blockIdx.y * BLK + threadIdx.y;
    int col = blockIdx.x * BLK + threadIdx.x;

    if (row < N && col < N) {
        float sum = 0.0f;

        for (int k = 0; k < N; k++)
            sum += A[row * N + k] * B[k * N + col];

        C[row * N + col] = sum;
    }
}
```

### 6.5 Timing and Verification

- CUDA events are used to measure kernel execution time on the GPU.
- A warm-up kernel launch is performed before timing.
- Transpose kernels are repeated 20 times, and the average time is calculated.
- Naive matrix multiplication is repeated 5 times, and the average time is calculated.
- The transpose output is checked against the CPU input.
- Twenty randomly selected matrix multiplication output elements are checked against a CPU reference calculation.

## 7. Compilation and Execution

### Linux / WSL / Google Colab

Compile the CUDA program:

```bash
nvcc -O2 -o exp6 exp6.cu
```

Run using the default matrix sizes:

```bash
./exp6
```

Run with custom matrix sizes:

```bash
./exp6 2048 512
```

The first argument specifies the transpose matrix size, and the second specifies the matrix multiplication size.

### Windows

Compile from a suitable Visual Studio Developer Command Prompt:

```powershell
nvcc -O2 -o exp6.exe exp6.cu
```

Run:

```powershell
.\exp6.exe
```

If required, specify the GPU architecture using the appropriate `-arch=sm_XX` option supported by the installed CUDA Toolkit and GPU.

## 8. Expected Output

The following is the **illustrative sample output from the lab manual**, not a measurement from every GPU.

```text
GPU: Tesla T4 (compute capability 7.5)

=== PART A: Matrix transpose (N = 4096) ===
Uncoalesced : 1.850 ms | 145.1 GB/s | PASS
Coalesced   : 0.720 ms | 372.8 GB/s | PASS
Speedup (uncoalesced / coalesced) = 2.57x

=== PART B: Naive matrix multiplication (N = 1024) ===
Naive matmul: 3.900 ms | 550.6 GFLOPS | PASS

=== SUMMARY ===
Transpose uncoalesced : 1.850 ms
Transpose coalesced   : 0.720 ms
Naive matmul          : 3.900 ms
```

Actual execution times and performance values depend on the GPU model, memory bandwidth, driver, CUDA version and system load.

## 9. Observation Table

Fill in this table using the values measured on the system.

| Kernel | Matrix size (N) | Time (ms) | Bandwidth (GB/s) / GFLOPS | Result |
|---|---:|---:|---:|---|
| Transpose: uncoalesced | 4096 | — | — | — |
| Transpose: coalesced | 4096 | — | — | — |
| Naive matrix multiplication | 1024 | — | — | — |

**Speedup of coalesced over uncoalesced transpose:** __________ ×

**GPU model:** __________________________

**Compute capability:** __________________

Run the program at least three times and record representative repeated measurements.

## 10. Analysis and Discussion

### Why is the coalesced transpose faster?

In the uncoalesced transpose, neighbouring threads write to addresses separated by `N` elements. This causes many separate global-memory transactions. The coalesced version uses shared memory to rearrange the tile, allowing both global-memory reads and writes to be contiguous.

### Why is padding used in shared memory?

The shared-memory tile is declared as `tile[32][33]` instead of `tile[32][32]`. The extra column helps avoid shared-memory bank conflicts when threads access the tile in transposed order.

### Why is naive matrix multiplication less efficient?

The naive kernel repeatedly reads matrix elements from global memory and does not reuse data through shared memory. Shared-memory tiling can reduce repeated global-memory accesses and improve performance.

### Why are CUDA events used for timing?

CUDA kernel launches are asynchronous with respect to the CPU. CUDA events measure execution time on the GPU. A warm-up launch and repeated measurements help reduce startup effects and timing noise.

## 11. Troubleshooting

| Problem | Possible Cause / Solution |
|---|---|
| `nvcc: command not found` | CUDA Toolkit may not be installed or `nvcc` may not be in the PATH. |
| No CUDA-capable device detected | Check the NVIDIA driver and GPU using `nvidia-smi`. |
| Transpose result shows FAIL | Check index calculations, swapped block coordinates and boundary conditions. |
| Very small speedup | The matrix may be too small. Try a larger transpose size such as `4096`. |
| Out of memory | Reduce matrix sizes, for example `./exp6 2048 512`. |


## 12. Conclusion

This experiment demonstrates that global-memory access patterns have a significant effect on CUDA kernel performance. The uncoalesced transpose performs strided writes, while the coalesced transpose uses shared memory to achieve more efficient global-memory access. The experiment also demonstrates naive matrix multiplication, CUDA event-based timing and result verification. Overall, coalesced memory access improves memory efficiency, and shared-memory data reuse is an important direction for further CUDA optimization.

---

**Student:** Krupa Akki  
**Department:** Computer Science and Engineering (Artificial Intelligence)  
**Institution:** K.L.E. Technological University, Hubli
