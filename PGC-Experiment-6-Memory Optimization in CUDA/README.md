Experiment 6: Memory Optimization in CUDA

A CUDA-based Parallel and Distributed Computing laboratory experiment demonstrating the impact of global memory access patterns, memory coalescing, shared memory, and GPU execution performance.

The experiment implements and compares three CUDA kernels:

Uncoalesced Matrix Transpose
Coalesced Matrix Transpose using Shared Memory
Naive Matrix Multiplication

The experiment measures GPU execution time using CUDA events, calculates effective memory bandwidth (GB/s), evaluates floating-point performance (GFLOPS), and verifies the correctness of GPU computations against expected CPU results.

Table of Contents
1. Aim
2. Objectives
3. Components and Configuration
4. Problem Definition
5. Theory
5.1 Memory Coalescing
5.2 Matrix Transpose
5.3 Shared Memory and Bank Conflicts
5.4 Naive Matrix Multiplication
6. System Architecture
7. Overall Execution Flow
8. CUDA Environment Setup
8.1 Prerequisites
8.2 GPU Verification
8.3 CUDA Compiler Verification
9. CUDA Implementation
9.1 Source Code
9.2 Part A - Uncoalesced Matrix Transpose
9.3 Part B - Coalesced Matrix Transpose
9.4 Part C - Naive Matrix Multiplication
9.5 CUDA Timing and Verification
10. Compilation and Execution
11. CUDA Execution Configuration
12. Results
12.1 Sample Output
12.2 Observation Table
13. Performance Analysis
13.1 Memory Bandwidth
13.2 GFLOPS Calculation
13.3 Speedup Calculation
13.4 Performance Graph
13.5 Observations
14. Troubleshooting
15. Conclusion
16. Viva Questions
17. Author
1. Aim

To study how GPU global-memory access patterns affect CUDA kernel performance by implementing uncoalesced and coalesced matrix transpose operations and naive matrix multiplication.

The experiment demonstrates how memory coalescing and shared memory improve memory access efficiency and GPU performance.

2. Objectives

The objectives of this experiment are:

To understand GPU global-memory access patterns.
To understand memory coalescing and its importance in CUDA programming.
To implement matrix transpose using uncoalesced global-memory access.
To implement optimized matrix transpose using shared memory.
To understand shared-memory bank conflicts and padding.
To implement naive matrix multiplication using CUDA.
To launch two-dimensional CUDA grids and thread blocks.
To measure GPU kernel execution time using CUDA events.
To calculate effective memory bandwidth in GB/s.
To calculate floating-point performance in GFLOPS.
To verify GPU computation results.
To compare the performance of coalesced and uncoalesced memory access.
3. Components and Configuration
3.1 Hardware Requirements
Component	Configuration
Host System	Windows / Linux
CPU	Multi-core processor
RAM	Sufficient memory for CUDA programs
GPU	NVIDIA CUDA-compatible GPU
GPU Memory	Sufficient for input and output matrices
Network	Internet connection for CUDA Toolkit installation or Google Colab
3.2 Software Requirements
Software	Purpose
Windows / Ubuntu	Operating environment
NVIDIA GPU Driver	GPU hardware support
CUDA Toolkit	CUDA development environment
NVCC	CUDA compiler
GCC / G++	Host-side compilation support
Visual Studio Build Tools	Windows host compiler support
Google Colab	Alternative cloud GPU environment
C / C++	Programming language
CUDA C/C++	GPU programming
3.3 CUDA Execution Configuration
Parameter	Value
Transpose Matrix Size	4096 × 4096
Matrix Multiplication Size	1024 × 1024
Transpose Tile Size	32 × 32
Matrix Multiplication Block	16 × 16
Transpose Repetitions	20
Matrix Multiplication Repetitions	5
Timing Method	CUDA Events
Memory Type	Global and Shared Memory
4. Problem Definition

The experiment studies the effect of memory access patterns on GPU performance.

Three different CUDA operations are performed.

Part A: Uncoalesced Matrix Transpose

A square matrix is transposed using direct global-memory access.

For an input matrix:

text
Input Matrix A:

1  2  3
4  5  6
7  8  9


The output matrix is:

text
Output Matrix B:

1  4  7
2  5  8
3  6  9


The transpose operation is defined as:

text
B[j][i] = A[i][j]

Part B: Coalesced Matrix Transpose

The same transpose operation is implemented using shared memory.

A 32 × 32 tile is loaded from global memory into shared memory. After synchronization, the tile is written to the output matrix using coalesced global-memory access.

Part C: Naive Matrix Multiplication

Two matrices A and B are multiplied to produce matrix C.

text
A = 1024 × 1024
B = 1024 × 1024
C = A × B


Each CUDA thread calculates one output element.

The mathematical operation is:

text
C[i][j] = Σ A[i][k] × B[k][j]


The computation is performed using a conventional triple-loop equivalent inside the CUDA kernel.

5. Theory
5.1 Memory Coalescing

Memory coalescing is an optimization technique used by GPUs to combine memory requests from threads within a warp.

A warp generally consists of 32 CUDA threads.

When consecutive threads access consecutive global-memory addresses, the GPU can combine their accesses into fewer memory transactions.

Coalesced Access
text
Thread 0  → Address 0
Thread 1  → Address 1
Thread 2  → Address 2
Thread 3  → Address 3
...
Thread 31 → Address 31


Consecutive threads access neighboring memory locations.

This results in efficient global-memory utilization.

Uncoalesced Access
text
Thread 0  → Address 0
Thread 1  → Address N
Thread 2  → Address 2N
Thread 3  → Address 3N
...
Thread 31 → Address 31N


Threads access memory locations separated by a large stride.

This can require many separate memory transactions and reduce effective bandwidth.

Comparison
Parameter	Coalesced	Uncoalesced
Memory Access	Consecutive	Strided
Memory Transactions	Fewer	More
Bandwidth Utilization	Efficient	Less efficient
Performance	Generally faster	Generally slower
5.2 Matrix Transpose

Matrix transpose exchanges the rows and columns of a matrix.

For an N × N matrix:

text
Output[j][i] = Input[i][j]


In row-major storage, the memory index of an element is:

text
index = row × N + column

Uncoalesced Transpose

In the uncoalesced implementation:

Each CUDA thread copies one matrix element.
Global-memory reads are consecutive.
Global-memory writes are separated by N elements.
The strided write pattern reduces memory efficiency.
Coalesced Transpose

In the coalesced implementation:

A 32 × 32 tile is loaded into shared memory.
Threads access consecutive global-memory locations.
__syncthreads() ensures all tile elements are loaded.
The tile is accessed in transposed order.
Output writes are also coalesced.
5.3 Shared Memory and Bank Conflicts

Shared memory is a fast, on-chip memory available to CUDA threads within a block.

It enables threads to reuse data without repeatedly accessing global memory.

The coalesced transpose uses:

cpp
__shared__ float tile[TILE][TILE + 1];


The extra column is known as padding.

Without padding, accessing the shared-memory tile in transposed order can cause bank conflicts.

Padding helps distribute accesses across different shared-memory banks.

The synchronization function:

cpp
__syncthreads();


ensures that all threads in the block finish loading the tile before any thread begins reading the transposed tile.

5.4 Naive Matrix Multiplication

The naive CUDA matrix multiplication kernel assigns one CUDA thread to each output element.

Each thread performs:

cpp
float sum = 0.0f;

for (int k = 0; k < N; k++)
{
    sum += A[row * N + k] * B[k * N + col];
}

C[row * N + col] = sum;


Characteristics:

Each thread calculates one element of C.
Each thread performs N iterations.
Each iteration accesses two global-memory elements.
No explicit shared-memory data reuse is implemented.
The kernel provides a baseline for future shared-memory tiling optimization.
6. System Architecture

The experiment uses three CUDA kernels to study GPU memory optimization.

mermaid
flowchart TD
    A["CUDA Memory Optimization Experiment"] --> B["Matrix Transpose"]
    A --> C["Naive Matrix Multiplication"]

    B --> D["Uncoalesced Transpose"]
    B --> E["Coalesced Transpose"]

    D --> F["Global Memory Access"]
    E --> G["Shared Memory Tile"]
    G --> H["Synchronization"]
    H --> I["Coalesced Global Memory Write"]

    C --> J["2D CUDA Grid"]
    J --> K["One Thread Per Output Element"]

    F --> L["Execution Time"]
    I --> L
    K --> L

    L --> M["Performance Comparison"]

6.1 Uncoalesced Transpose Architecture
text
          Host CPU
             |
       Input Matrix
             |
       Global Memory
             |
       CUDA Kernel
             |
      +------+------+
      |      |      |
    Warp   Warp   Warp
      |      |      |
      +------+------+
             |
      Strided Global Writes
             |
       Output Matrix

6.2 Coalesced Transpose Architecture
text
          Host CPU
             |
       Input Matrix
             |
       Global Memory
             |
      Coalesced Read
             |
       Shared Memory
        32 × 32 Tile
             |
       __syncthreads()
             |
       Transposed Access
             |
      Coalesced Write
             |
       Output Matrix

6.3 Naive Matrix Multiplication Architecture
text
          Host CPU
             |
       Matrices A and B
             |
       Global Memory
             |
        CUDA Grid
             |
       +-----+-----+
       |     |     |
      Block Block Block
       |     |     |
      Threads Threads
       |     |     |
       +-----+-----+
             |
     Naive Matrix Multiplication
             |
         Matrix C
             |
          Host CPU

7. Overall Execution Flow
text
          Start Experiment
                 |
                 v
       Verify NVIDIA GPU
                 |
                 v
       Verify CUDA Toolkit
                 |
                 v
        Create exp6.cu
                 |
                 v
       Initialize Host Matrices
                 |
                 v
        Copy Data to GPU
                 |
          +------+------+
          |             |
          v             v
    Uncoalesced       Coalesced
     Transpose         Transpose
          |             |
          v             v
       CUDA Events and Timing
          |             |
          +------+------+
                 |
                 v
        Verify Transpose Results
                 |
                 v
       Naive Matrix Multiplication
                 |
                 v
          Measure GFLOPS
                 |
                 v
         Verify Matrix Result
                 |
                 v
       Performance Comparison
                 |
                 v
                End

8. CUDA Environment Setup
8.1 Prerequisites

The experiment can be performed using either:

A local computer with an NVIDIA GPU and CUDA Toolkit.
Google Colab with a GPU runtime.

Required components:

NVIDIA GPU driver
CUDA Toolkit
NVCC compiler
C/C++ compiler
Terminal or command prompt
8.2 GPU Verification

Open Windows PowerShell or an Ubuntu terminal.

Run:

bash
nvidia-smi


This displays:

GPU model
GPU memory
Driver version
CUDA compatibility information
GPU utilization

The GPU should be detected successfully.

8.3 CUDA Compiler Verification

Run:

bash
nvcc --version


The CUDA compiler version should be displayed.

Example:

text
Cuda compilation tools, release XX.X


The actual version depends on the installed CUDA Toolkit.

9. CUDA Implementation
9.1 Source Code

The complete CUDA source code is available in:

text
cuda/exp6_cuda_memory.cu


The program contains:

CUDA error-checking macro.
Uncoalesced transpose kernel.
Coalesced transpose kernel.
Naive matrix multiplication kernel.
CUDA event-based timing functions.
Result verification functions.
Host and device memory allocation.
Kernel execution and performance calculations.
9.2 Part A - Uncoalesced Matrix Transpose

The first CUDA kernel performs matrix transpose using direct global-memory access.

Kernel:

cpp
__global__ void transposeNaive(
    const float *in,
    float *out,
    int N)
{
    int x = blockIdx.x * TILE + threadIdx.x;
    int y = blockIdx.y * TILE + threadIdx.y;

    if (x < N && y < N)
        out[x * N + y] = in[y * N + x];
}


Explanation:

blockIdx identifies the CUDA block.
threadIdx identifies the thread inside the block.
Each thread processes one matrix element.
Reads are consecutive.
Writes are strided.

The kernel demonstrates the effect of uncoalesced global-memory writes.

9.3 Part B - Coalesced Matrix Transpose

The second CUDA kernel improves global-memory access using shared memory.

Kernel:

cpp
__global__ void transposeCoalesced(
    const float *in,
    float *out,
    int N)
{
    __shared__ float tile[TILE][TILE + 1];

    int x = blockIdx.x * TILE + threadIdx.x;
    int y = blockIdx.y * TILE + threadIdx.y;

    if (x < N && y < N)
        tile[threadIdx.y][threadIdx.x] =
            in[y * N + x];

    __syncthreads();

    x = blockIdx.y * TILE + threadIdx.x;
    y = blockIdx.x * TILE + threadIdx.y;

    if (x < N && y < N)
        out[y * N + x] =
            tile[threadIdx.x][threadIdx.y];
}


Explanation:

A shared-memory tile stores matrix elements.
Global-memory reads are coalesced.
Synchronization ensures the tile is completely loaded.
Block coordinates are exchanged during output.
The transposed tile is written using coalesced global-memory access.
Padding helps avoid shared-memory bank conflicts.
9.4 Part C - Naive Matrix Multiplication

The third kernel performs matrix multiplication on the GPU.

Kernel:

cpp
__global__ void matMulNaive(
    const float *A,
    const float *B,
    float *C,
    int N)
{
    int row = blockIdx.y * BLK + threadIdx.y;
    int col = blockIdx.x * BLK + threadIdx.x;

    if (row < N && col < N)
    {
        float sum = 0.0f;

        for (int k = 0; k < N; k++)
        {
            sum += A[row * N + k] *
                   B[k * N + col];
        }

        C[row * N + col] = sum;
    }
}


Explanation:

Each CUDA thread calculates one output element.
Each thread executes a loop of N iterations.
Two global-memory values are read in each iteration.
The multiplication and accumulation produce the output element.
Shared-memory tiling is not used in this baseline kernel.
9.5 CUDA Timing and Verification

The experiment uses CUDA events to measure kernel execution time.

The following CUDA event functions are used:

cpp
cudaEventCreate()
cudaEventRecord()
cudaEventSynchronize()
cudaEventElapsedTime()
cudaEventDestroy()


The program performs a warm-up kernel launch before recording execution time.

Transpose Timing
One warm-up launch.
Twenty timed repetitions.
Average execution time is calculated.
Matrix Multiplication Timing
One warm-up launch.
Five timed repetitions.
Average execution time is calculated.
Result Verification

The transpose results are compared against the expected CPU transpose.

The matrix multiplication results are checked against CPU reference calculations at 20 randomly selected positions.

The program reports:

text
PASS


when verification succeeds.

10. Compilation and Execution
10.1 Create the Project Directory
bash
mkdir -p ~/parallel_lab/exp6/cuda
cd ~/parallel_lab/exp6/cuda

10.2 Create the Source File

Create:

bash
nano exp6.cu


Paste the complete CUDA source code from:

text
exp6_cuda_memory.cu


Save the file.

10.3 Compile the CUDA Program

On Linux or Google Colab:

bash
nvcc -O2 -o exp6 exp6.cu


On Windows:

bash
nvcc -O2 -o exp6.exe exp6.cu


If required, specify the GPU architecture using:

bash
nvcc -O2 -arch=sm_XX -o exp6 exp6.cu


Replace sm_XX with an architecture supported by the installed CUDA Toolkit and target GPU.

10.4 Execute the Program

On Linux:

bash
./exp6


On Windows:

bash
exp6.exe


The default matrix sizes are:

text
Transpose Matrix = 4096 × 4096
Matrix Multiplication = 1024 × 1024

10.5 Execute with Custom Matrix Sizes

The program accepts two command-line arguments.

Example:

bash
./exp6 2048 512


This executes:

text
Transpose Matrix = 2048 × 2048
Matrix Multiplication = 512 × 512

10.6 Google Colab Execution
Open Google Colab.
Select Runtime.
Select Change runtime type.
Choose GPU.
Save the configuration.
Verify GPU availability:
python
!nvidia-smi

Create the CUDA source file using %%writefile exp6.cu.
Paste the complete source code.
Compile:
python
!nvcc -O2 -o exp6 exp6.cu

Execute:
python
!./exp6

11. CUDA Execution Configuration
11.1 Matrix Transpose

Default transpose matrix:

text
N = 4096


Tile configuration:

text
TILE = 32
Block = 32 × 32


Grid configuration:

text
Grid X = 4096 / 32 = 128
Grid Y = 4096 / 32 = 128


Therefore:

text
Grid = 128 × 128 blocks


Total blocks:

text
128 × 128 = 16,384 blocks


Each block contains:

text
32 × 32 = 1,024 threads

11.2 Naive Matrix Multiplication

Default matrix size:

text
N = 1024


Block configuration:

text
BLK = 16
Block = 16 × 16


Grid configuration:

text
Grid X = 1024 / 16 = 64
Grid Y = 1024 / 16 = 64


Therefore:

text
Grid = 64 × 64 blocks


Total blocks:

text
64 × 64 = 4,096 blocks


Each block contains:

text
16 × 16 = 256 threads


Total logical thread instances:

text
1024 × 1024 = 1,048,576


Each logical thread computes one element of matrix C.

12. Results

The experiment measures the execution time and performance of three CUDA kernels.

The expected results are:

Both transpose kernels should produce correct transposed matrices.
The coalesced transpose should generally outperform the uncoalesced transpose.
The naive matrix multiplication should produce correct output values.
The effective bandwidth and GFLOPS should be calculated from measured execution times.
12.1 Sample Output

The following is illustrative sample output from the laboratory manual using an NVIDIA Tesla T4 GPU. Actual values depend on GPU hardware, driver, clock frequency, and system configuration.

text
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


Note: These are reference values, not actual measured results from every GPU.

12.2 Observation Table

The following table should be filled using the actual execution output.

Kernel	Matrix Size	Time (ms)	Bandwidth / GFLOPS	Result
Transpose: Uncoalesced	4096	To be recorded	To be recorded	PASS/FAIL
Transpose: Coalesced	4096	To be recorded	To be recorded	PASS/FAIL
Naive Matrix Multiplication	1024	To be recorded	To be recorded	PASS/FAIL

Coalesced transpose speedup: To be calculated from actual results.

GPU Model: To be recorded.

Compute Capability: To be recorded.

13. Performance Analysis
13.1 Memory Bandwidth

Effective memory bandwidth for matrix transpose is calculated using:

text
Bandwidth = Total Data Transferred / Execution Time


Each transpose performs:

One global-memory read.
One global-memory write.

Therefore:

text
Bandwidth = (2 × N × N × 4) / Time


Where:

N = Matrix dimension.
4 = Bytes per float.
Time = Average kernel execution time in seconds.

When time is measured in milliseconds, the result is converted to GB/s.

Formula:

text
Bandwidth (GB/s) =
(2 × N × N × 4) / (Time_ms × 1,000,000)


A higher effective bandwidth indicates better global-memory utilization.

13.2 GFLOPS Calculation

GFLOPS measures floating-point operations performed per second.

For matrix multiplication:

text
C = A × B


The total floating-point operations are approximately:

text
FLOPs = 2 × N³


Therefore:

text
GFLOPS = (2 × N³) / (Time_ms × 1,000,000)


For a 1024 × 1024 matrix multiplication, the number of floating-point operations is:

text
2 × 1024³


The calculated GFLOPS value represents the average floating-point performance of the naive matrix multiplication kernel.

13.3 Speedup Calculation

The speedup of the coalesced transpose compared with the uncoalesced transpose is:

text
Speedup = Uncoalesced Time / Coalesced Time


Using the illustrative sample values:

text
Speedup = 1.850 / 0.720

Speedup = 2.57×


Therefore, the coalesced transpose is approximately 2.57 times faster in the sample experiment.

13.4 Performance Graph

The following graph represents the illustrative transpose execution times.

mermaid
xychart-beta
    title "Transpose Execution Time Comparison"
    x-axis ["Uncoalesced", "Coalesced"]
    y-axis "Execution Time (ms)" 0 --> 2
    bar [1.850, 0.720]


The coalesced implementation achieves lower execution time by improving global-memory access patterns.

13.5 Observations
Uncoalesced Transpose

The uncoalesced implementation reads consecutive global-memory elements but writes elements separated by a large stride.

This creates inefficient global-memory transactions and reduces effective memory bandwidth.

Coalesced Transpose

The coalesced implementation uses a shared-memory tile to reorganize matrix elements.

Both global-memory reads and writes are performed using consecutive addresses.

This improves memory access efficiency and generally reduces execution time.

Shared Memory Padding

The shared-memory array is declared as:

cpp
__shared__ float tile[32][33];


The extra column reduces shared-memory bank conflicts during transposed tile access.

Naive Matrix Multiplication

The naive matrix multiplication kernel assigns one output element to each CUDA thread.

Although neighboring threads access consecutive columns of matrix B, the kernel does not explicitly reuse matrix data through shared memory.

Consequently, the same input elements may be loaded repeatedly by different threads.

This limits memory efficiency and makes the kernel a useful baseline for future optimization.

CUDA Event Timing

CUDA kernel launches are asynchronous.

Therefore, ordinary CPU timing around a kernel launch does not necessarily measure the actual GPU execution time.

CUDA events measure execution time on the GPU.

Warm-up launches and repeated measurements help reduce initialization overhead and timing variations.

14. Troubleshooting
Problem	Possible Solution
nvcc: command not found	Install CUDA Toolkit and configure PATH.
nvidia-smi fails	Verify NVIDIA driver installation and GPU availability.
No CUDA-capable device detected	Check the GPU driver or enable GPU runtime in Colab.
CUDA compilation fails	Verify CUDA Toolkit and supported host compiler versions.
Result shows FAIL	Check matrix indexing, block coordinates, and bounds conditions.
Coalesced kernel is not faster	Increase matrix size and repeat the experiment.
Very small speedup	Check GPU utilization and ensure the workload is large enough.
Out of memory	Reduce matrix dimensions, for example ./exp6 2048 512.
Shared-memory errors	Check tile dimensions and synchronization.
Incorrect transpose output	Verify swapped block coordinates and shared-memory indexing.
CUDA events return unexpected times	Ensure warm-up and synchronization are performed correctly.
15. Conclusion

This experiment demonstrated how global-memory access patterns influence CUDA GPU performance.

Three CUDA kernels were implemented:

Uncoalesced matrix transpose using direct global-memory access.
Coalesced matrix transpose using shared memory.
Naive matrix multiplication using a two-dimensional CUDA grid.

The uncoalesced transpose demonstrated the performance limitations of strided global-memory writes.

The coalesced transpose improved memory access efficiency by loading matrix tiles into shared memory, synchronizing threads, and writing transposed data using coalesced global-memory accesses.

The naive matrix multiplication demonstrated how a GPU kernel without explicit shared-memory data reuse can repeatedly access global memory.

CUDA events were used to measure kernel execution time, while effective bandwidth and GFLOPS were calculated to evaluate performance.

The experiment demonstrates that efficient memory access, coalescing, shared-memory optimization, and proper synchronization are important factors in improving GPU application performance.

16. Viva Questions
What is memory coalescing in CUDA?
What is a warp in GPU architecture?
What is the difference between coalesced and uncoalesced memory access?
Why is the uncoalesced transpose slower?
What is shared memory in CUDA?
Why is __syncthreads() required in the coalesced transpose?
What is a shared-memory bank conflict?
Why is an extra column used in tile[32][33]?
What is the purpose of CUDA events?
Why is a warm-up kernel launch performed before timing?
What is the difference between global memory and shared memory?
What does GFLOPS represent?
How is effective memory bandwidth calculated?
How many global-memory reads does each thread perform in naive matrix multiplication for N = 1024?
How can shared-memory tiling improve matrix multiplication performance?
17. Author

Krupa

CSE (Artificial Intelligence)
K.L.E. Technological University, Hubli

Repository Structure
text
Experiment-6-Memory-Optimization-CUDA/
│
├── README.md
│
├── cuda/
│   └── exp6_cuda_memory.cu
│
└── screenshots/
    ├── 01_GPU_Verification.png
    ├── 02_CUDA_Compilation.png
    ├── 03_Uncoalesced_Transpose.png
    ├── 04_Coalesced_Transpose.png
    └── 05_Final_Results.png

Result Screenshots
1. GPU Verification

!GPU Verification

2. CUDA Compilation

!CUDA Compilation

3. Uncoalesced Matrix Transpose

!Uncoalesced Transpose

4. Coalesced Matrix Transpose

!Coalesced Transpose

5. Final Results

!Final Results

Experiment 6: Memory Optimization in CUDA
Subject: Memory Systems and Synchronization
Implementation: CUDA C/C++
