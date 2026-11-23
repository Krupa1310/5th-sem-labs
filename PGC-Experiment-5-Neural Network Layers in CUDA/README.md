PGC Experiment 5 - Neural Network Layers in CUDA

A Parallel and Distributed Computing laboratory experiment implementing basic neural-network layers using custom CUDA kernels.

The experiment implements and compares:

Matrix multiplication with bias using a custom CUDA kernel.
ReLU activation using CUDA.
Sigmoid activation using CUDA.
A two-layer neural-network forward pass on CPU and GPU.
Numerical correctness validation between CPU and GPU outputs.
GPU kernel-only and end-to-end execution time.
GPU speedup calculation.

The experiment demonstrates how CUDA parallelism accelerates neural-network computations by distributing matrix and activation operations across GPU threads.

Table of Contents
Problem Statement
Objectives
Components and Configuration
Theory
4.1 Neural Network Forward Pass
4.2 Matrix Multiplication with Bias
4.3 ReLU Activation
4.4 Sigmoid Activation
4.5 CUDA Programming Model
4.6 CPU and GPU Execution
System Architecture
Installation and Environment Setup
6.1 NVIDIA GPU Driver
6.2 CUDA Toolkit
6.3 Visual Studio Build Tools
6.4 Developer Command Prompt
6.5 System Verification
Part A - CUDA Kernel Implementation
Part B - CPU Implementation
Part C - GPU Forward Pass
Part D - Performance Evaluation
Execution Steps
Expected Output
Experimental Results
Observation and Comparison
Limitations
Troubleshooting
Precautions
Conclusion
Author


1. Problem Statement

Neural networks perform computations involving matrix multiplication, bias addition, and activation functions.

In traditional CPU execution, these operations are performed using sequential or CPU-based parallel processing. GPUs provide thousands of parallel processing threads that can accelerate computationally intensive neural-network operations.

This experiment implements a two-layer neural network using custom CUDA kernels.

The network performs the following operations:

Layer 1:

Z1 = X × W1 + b1

A1 = ReLU(Z1)

Layer 2:

Z2 = A1 × W2 + b2

Y = Sigmoid(Z2)

The same forward pass is implemented on both CPU and GPU.

The experiment compares execution times, validates numerical correctness, and calculates GPU speedup.

This experiment performs inference only. It does not implement training, loss calculation, optimization, or backpropagation.

2. Objectives

The objectives of this experiment are:

To understand CUDA kernels, blocks, threads, and grid dimensions.
To implement matrix multiplication with bias using CUDA.
To implement ReLU activation using CUDA.
To implement sigmoid activation using CUDA.
To understand GPU memory allocation and data transfer.
To execute neural-network operations on CPU and GPU.
To validate CPU and GPU numerical results.
To measure CPU and GPU execution time.
To calculate kernel-only and end-to-end GPU speedup.
To understand the performance benefits of GPU parallelism.
3. Components and Configuration
3.1 Hardware Configuration
Component	Configuration
Host System	Windows 10/11
GPU	NVIDIA CUDA-capable GPU
Demonstrated GPU	NVIDIA RTX 4500 Ada Generation
CPU	System processor
System Memory	Sufficient RAM for CUDA execution
GPU Memory	Sufficient VRAM for network tensors
3.2 Software Requirements
Software / Tool	Purpose
Windows 10/11	Operating system
NVIDIA GPU Driver	GPU communication
CUDA Toolkit 13.0	CUDA compilation and runtime
NVIDIA NVCC	CUDA compiler
Visual Studio 2022 Build Tools	C++ compilation
MSVC v143	C++ compiler
Windows SDK	Windows development support
Developer Command Prompt	CUDA compilation environment
Notepad	Source code editing
Git	Version control
GitHub	Source code and documentation
3.3 Compiler and Runtime Configuration
Component	Configuration
CUDA Toolkit	13.0
Compiler	NVCC
C++ Compiler	MSVC v143
Build Configuration	-O2
Source File	neural_network.cu
Executable	neural_network.exe
Batch Size	256
Input Size	128
Hidden Layer Size	64
Output Size	10
Repetitions	20
Floating-Point Type	float
CUDA Block Dimensions	16 × 16 for matrix kernels
4. Theory
4.1 Neural Network Forward Pass

A forward pass calculates the output of a neural network by passing input data through multiple layers.

This experiment uses a two-layer feed-forward neural network.

First Layer:

Z1 = X × W1 + b1

A1 = ReLU(Z1)

Second Layer:

Z2 = A1 × W2 + b2

Y = Sigmoid(Z2)

Where:

X represents the input matrix.
W1 and W2 represent weight matrices.
b1 and b2 represent bias vectors.
Z1 and Z2 represent intermediate outputs.
A1 represents the hidden-layer activation.
Y represents the final network output.
4.2 Matrix Multiplication with Bias

Matrix multiplication combines input values with weights to produce output values.

For matrices A and B:

A has dimensions M × K.
B has dimensions K × N.
C has dimensions M × N.

The operation is:

C[row, col] = Σ A[row, k] × B[k, col] + bias[col]

In CUDA, each thread calculates one output matrix element.

Thread indexing uses:

blockIdx: Identifies the block.
blockDim: Specifies the number of threads in a block.
threadIdx: Identifies the thread within a block.

Boundary checks prevent threads from accessing invalid matrix positions.

4.3 ReLU Activation

ReLU stands for Rectified Linear Unit.

Mathematical expression:

ReLU(x) = max(0, x)

It replaces negative values with zero while preserving positive values.

Example:

Input: [-2, 0, 3, -4, 5]

Output: [0, 0, 3, 0, 5]

Each CUDA thread processes one array element.

4.4 Sigmoid Activation

The sigmoid function converts real-valued inputs into values between 0 and 1.

Mathematical expression:

Sigmoid(x) = 1 / (1 + exp(-x))

Example:

Input	Output
-2	0.119203
0	0.500000
2	0.880797

Each CUDA thread calculates one sigmoid output.

4.5 CUDA Programming Model

CUDA is NVIDIA's parallel computing platform.

Its execution model contains:

Grid: Collection of thread blocks.
Block: Collection of CUDA threads.
Thread: Smallest execution unit.
Kernel: Function executed on the GPU.

A CUDA kernel is launched using the following syntax:

cpp
kernelName<<<grid, block>>>(arguments);


For matrix multiplication, the experiment uses:

cpp
dim3 block(16, 16);


Each block contains 256 threads.

The grid dimensions are calculated based on the output matrix dimensions.

4.6 CPU and GPU Execution

CPU Execution:

Uses ordinary C++ functions.
Performs matrix multiplication using nested loops.
Applies ReLU and sigmoid sequentially.
Calculates the reference output.

GPU Execution:

Allocates device memory.
Copies inputs, weights, and biases to the GPU.
Launches CUDA kernels.
Executes matrix multiplication and activation operations.
Copies the final output back to the CPU.

CUDA kernels launched on the same default stream execute in launch order, preserving the forward-pass dependency.

5. System Architecture
5.1 Overall Experiment Architecture
text
              Input Matrix X
                     |
                     |
             First Layer
                     |
          Matrix Multiplication
                     |
               Bias Addition
                     |
               ReLU Kernel
                     |
              Hidden Layer
                     |
          Matrix Multiplication
                     |
               Bias Addition
                     |
             Sigmoid Kernel
                     |
                     |
              Final Output
                     |
          +----------+----------+
          |                     |
       CPU Output           GPU Output
          |                     |
          +----------+----------+
                     |
              Result Validation
                     |
              Maximum Difference
                     |
              Performance Analysis
                     |
               Speedup Calculation

5.2 Network Configuration

The experiment uses deterministic input and weight values generated using sine and cosine functions.

This ensures that CPU and GPU receive identical input data.

Parameter	Value
BATCH	256
INPUT_SIZE	128
HIDDEN_SIZE	64
OUTPUT_SIZE	10
REPEATS	20
5.3 Tensor Dimensions
Tensor	Dimensions
Input X	256 × 128
Weight W1	128 × 64
Bias b1	64
Hidden Activation A1	256 × 64
Weight W2	64 × 10
Bias b2	10
Final Output Y	256 × 10
6. Installation and Environment Setup
6.1 NVIDIA GPU Driver

Open PowerShell and execute:

powershell
nvidia-smi


This displays:

GPU name.
NVIDIA driver version.
CUDA compatibility version.
GPU memory usage.
GPU utilization.

The system must detect an NVIDIA CUDA-capable GPU.

6.2 CUDA Toolkit

Install the NVIDIA CUDA Toolkit.

Verify the CUDA compiler:

powershell
nvcc --version


Find the CUDA compiler location:

powershell
where.exe nvcc


The output should show a path similar to:

text
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\nvcc.exe

6.3 Visual Studio Build Tools

Install Visual Studio 2022 Build Tools.

Select the following workload:

Desktop development with C++

Ensure the following components are installed:

MSVC v143 x64/x86 build tools.
Windows 10 SDK or Windows 11 SDK.

CUDA requires the Microsoft C++ compiler to compile the host-side code.

6.4 Developer Command Prompt

Open:

Developer Command Prompt for VS 2022

Alternatively, open:

x64 Native Tools Command Prompt for VS 2022.

Verify the C++ compiler:

cmd
where cl


Execute:

cmd
cl


The compiler version and usage information should appear.

Important: All compilation and execution commands should be performed using the Developer Command Prompt.

6.5 System Verification

Run the following commands:

cmd
nvidia-smi
nvcc --version
where.exe nvcc
where cl


Verify that the GPU, CUDA compiler, and Microsoft C++ compiler are available before continuing.

7. Part A - CUDA Kernel Implementation

The first part implements three custom CUDA kernels.

Source file:

text
neural_network.cu

7.1 Matrix Multiplication with Bias

The matrix multiplication kernel calculates one output element per CUDA thread.

The thread calculates its row and column using:

cpp
int row = blockIdx.y * blockDim.y + threadIdx.y;
int col = blockIdx.x * blockDim.x + threadIdx.x;


The kernel performs multiplication and bias addition:

cpp
float sum = 0.0f;

for (int k = 0; k < K; ++k) {
    sum += A[row * K + k] * B[k * N + col];
}

C[row * N + col] = sum + bias[col];


Boundary checking ensures that only valid output positions are processed.

7.2 ReLU Kernel

The ReLU kernel applies the activation function to every element.

cpp
values[idx] = fmaxf(0.0f, values[idx]);


Each thread processes one element.

7.3 Sigmoid Kernel

The sigmoid kernel calculates:

cpp
values[idx] = 1.0f / (1.0f + expf(-values[idx]));


Each CUDA thread processes one element independently.

8. Part B - CPU Implementation

The CPU implementation acts as the reference implementation.

The following functions are used:

Function	Purpose
cpuMatMulBias()	Matrix multiplication with bias
cpuReLU()	ReLU activation
cpuSigmoid()	Sigmoid activation
cpuForwardPass()	Complete neural-network forward pass

The CPU performs the following operations:

Multiply input X with W1.
Add bias b1.
Apply ReLU.
Multiply hidden activation with W2.
Add bias b2.
Apply sigmoid.
Store the final output.

The CPU forward pass is executed 20 times, and the average execution time is calculated.

9. Part C - GPU Forward Pass

The GPU implementation executes the same neural-network operations using CUDA kernels.

9.1 GPU Memory Allocation

The program allocates memory using:

cpp
cudaMalloc()


The following device arrays are allocated:

dX
dW1
db1
dZ1
dW2
db2
dZ2
9.2 Host-to-Device Data Transfer

Input matrices, weight matrices, and bias vectors are transferred from CPU memory to GPU memory using:

cpp
cudaMemcpy()


The transfer direction is:

cpp
cudaMemcpyHostToDevice

9.3 Kernel Launch

The GPU forward pass launches four kernels in sequence:

Matrix multiplication with bias.
ReLU activation.
Matrix multiplication with bias.
Sigmoid activation.

The function used is:

cpp
launchGpuForwardPass()

9.4 Device-to-Host Data Transfer

After the GPU computation is completed, the final output is copied back to CPU memory.

The transfer direction is:

cpp
cudaMemcpyDeviceToHost


The CPU and GPU output arrays are then compared.

10. Part D - Performance Evaluation

The experiment measures three execution times.

10.1 CPU Execution Time

The CPU performs the complete forward pass 20 times.

The average execution time is calculated using:

cpp
std::chrono::steady_clock

10.2 GPU Kernel-Only Execution Time

CUDA events are used to measure GPU kernel execution time.

This measurement includes the repeated kernel launches and GPU computation.

It excludes the initial host-to-device data transfers and final output transfer.

10.3 GPU End-to-End Execution Time

The end-to-end measurement includes:

Input data transfer.
Weight transfer.
Bias transfer.
GPU kernel execution.
GPU synchronization.
Output transfer back to CPU.

Therefore, end-to-end execution time represents the complete GPU computation workflow.

10.4 Speedup Calculation

Kernel-only speedup:

text
CPU Time / GPU Kernel-Only Time


End-to-end speedup:

text
CPU Time / GPU End-to-End Time


A speedup greater than 1 indicates that the GPU execution is faster than the CPU execution for the corresponding measurement.

11. Execution Steps

The following commands summarize the complete experiment.

Step	Command	Purpose
1	nvidia-smi	Check NVIDIA GPU
2	nvcc --version	Verify CUDA compiler
3	where cl	Verify MSVC compiler
4	mkdir "%USERPROFILE%\Documents\Experiment5_CUDA"	Create project directory
5	cd /d "%USERPROFILE%\Documents\Experiment5_CUDA"	Navigate to directory
6	notepad neural_network.cu	Create CUDA source file
7	Paste all 8 code phases	Complete program implementation
8	nvcc -c neural_network.cu	Check partial compilation after Phase 5
9	nvcc -O2 neural_network.cu -o neural_network.exe	Compile complete CUDA program
10	dir neural_network.exe	Verify executable
11	neural_network.exe	Execute experiment
12	nvidia-smi	Inspect GPU utilization
Complete Execution Sequence

After completing all eight code phases, execute:

cmd
nvcc -O2 neural_network.cu -o neural_network.exe


Run the program:

cmd
neural_network.exe


The program performs individual kernel tests, CPU execution, GPU execution, numerical comparison, and speedup calculation.

12. Expected Output

The following is the reference output from the demonstrated NVIDIA RTX 4500 Ada Generation GPU.

text
EXPERIMENT 5: NEURAL NETWORK LAYERS IN CUDA

GPU detected: NVIDIA RTX 4500 Ada Generation

Testing individual CUDA kernels...

Matrix multiplication + bias: PASSED
ReLU: PASSED
Sigmoid: PASSED

Forward-pass dimensions:
Input: 256 x 128
Hidden layer: 256 x 64
Output: 256 x 10

Average CPU compute time: 0.526860 ms
Average GPU kernel-only time: 0.026517 ms
Average GPU end-to-end time: 0.066010 ms

Kernel-only speedup: 19.868913x
End-to-end speedup: 7.981518x

Maximum absolute output difference: 0.000000

CPU and GPU outputs: MATCH (within tolerance)

First 10 output values (GPU):
0.498196 0.503101 0.508006 0.512911 0.517814
0.497729 0.502638 0.507548 0.512457 0.517364


Note: Execution times depend on the GPU, CPU, driver, CUDA Toolkit, and system load. The values above are reference measurements and should not be reported as measurements from another computer.

13. Experimental Results
13.1 Individual CUDA Kernel Tests
Kernel	Expected Result	Status
Matrix Multiplication + Bias	[23, 27, 50, 63]	PASSED
ReLU	[0, 0, 3, 0, 5]	PASSED
Sigmoid	[0.119203, 0.5, 0.880797]	PASSED
13.2 CPU and GPU Performance Comparison
Measurement	Reference Result	Unit
CPU Average Compute Time	0.526860	ms
GPU Kernel-Only Time	0.026517	ms
GPU End-to-End Time	0.066010	ms
Kernel-Only Speedup	19.868913	×
End-to-End Speedup	7.981518	×
13.3 Numerical Correctness
Parameter	Result
Maximum Absolute Difference	0.000000
Allowed Tolerance	0.0001
CPU and GPU Outputs	MATCH
Matrix Kernel Test	PASSED
ReLU Kernel Test	PASSED
Sigmoid Kernel Test	PASSED
13.4 Speedup Comparison

The recorded experiment achieved:

Approximately 19.87× kernel-only speedup.
Approximately 7.98× end-to-end speedup.

The kernel-only speedup is higher because it excludes data-transfer overhead.

14. Observation and Comparison
Case	Correctness	Performance Observation
Matrix Multiplication	Correct	Parallel output computation using CUDA threads
ReLU Activation	Correct	Independent element-wise processing
Sigmoid Activation	Correct	Parallel activation computation
CPU Forward Pass	Correct	Sequential C++ implementation
GPU Forward Pass	Correct	Parallel execution using CUDA kernels
Kernel-Only Timing	Measured	Excludes data-transfer overhead
End-to-End Timing	Measured	Includes memory transfers and kernel execution
Numerical Validation	MATCH	GPU output agrees with CPU output within tolerance
Important Observations
CUDA kernels allow multiple matrix elements to be calculated in parallel.
Each CUDA thread processes an individual output element or activation value.
Matrix multiplication with bias forms the main computational part of the neural network.
ReLU and sigmoid are element-wise activation functions.
GPU execution produces results numerically equivalent to CPU execution within the specified tolerance.
GPU kernel-only execution is faster than the CPU reference execution in the demonstrated run.
End-to-end execution includes data-transfer overhead.
End-to-end speedup is lower than kernel-only speedup.
GPU warm-up reduces the influence of first-launch initialization overhead.
Execution times can vary across different systems and repeated runs.
15. Limitations

The experiment has the following limitations:

It requires an NVIDIA CUDA-capable GPU.
The implementation uses custom CUDA kernels rather than optimized deep-learning libraries such as cuBLAS.
The matrix multiplication kernel uses a simple direct computation approach.
The experiment implements only a two-layer neural-network forward pass.
Neural-network training and backpropagation are not implemented.
GPU performance depends on the hardware configuration.
Data-transfer overhead can reduce the overall GPU speedup.
Floating-point calculations may produce small CPU/GPU numerical differences.
Timing measurements can vary between executions.
The experiment uses fixed network dimensions and deterministic input values.
16. Troubleshooting
Problem	Solution
nvidia-smi is not recognized	Install or verify the NVIDIA GPU driver
nvcc is not recognized	Install CUDA Toolkit and verify PATH
Cannot find compiler cl.exe in PATH	Open Developer Command Prompt for VS 2022
where cl returns no result	Install Visual Studio C++ build tools
LNK1104 cannot open file	Move the project to Documents and close any running executable
No CUDA device detected	Check GPU driver installation and CUDA compatibility
CUDA kernel test fails	Verify indexing, memory allocation, and kernel launch dimensions
CPU/GPU outputs do not match	Verify tensor dimensions, data transfers, and computation
Executable not generated	Check NVCC compilation errors
Execution times vary	Repeat the experiment and record the actual measurements
17. Precautions
Use an NVIDIA CUDA-capable GPU.
Ensure the NVIDIA GPU driver and CUDA Toolkit are properly installed.
Use Developer Command Prompt for VS 2022 for compilation.
Verify that nvcc and cl.exe are available.
Save the source file with the .cu extension.
Store the project in a user-writable directory such as Documents.
Do not paste any code phase more than once.
Verify all three CUDA kernel tests before performance evaluation.
Check CUDA errors during memory allocation and kernel execution.
Record actual execution times from your own system.
Run the experiment multiple times to observe timing variations.
Ensure CPU and GPU output validation succeeds before drawing conclusions.
18. Conclusion

This experiment implemented and evaluated basic neural-network layers using custom CUDA kernels.

Matrix multiplication with bias, ReLU activation, and sigmoid activation were implemented and tested independently.

The three CUDA kernels were then combined to execute a two-layer neural-network forward pass on the GPU. The same computation was performed on the CPU to validate numerical correctness.

The experiment measured CPU execution time, GPU kernel-only execution time, and GPU end-to-end execution time.

In the demonstrated run, all three CUDA kernel tests passed, and CPU and GPU outputs matched within the specified numerical tolerance.

The GPU achieved approximately 19.87× kernel-only speedup and 7.98× end-to-end speedup compared with the CPU reference implementation.

Overall, the experiment provided practical understanding of CUDA programming, GPU memory management, parallel execution, neural-network computations, numerical validation, and GPU performance evaluation.

19. Author

Krupa1310

CSE (Artificial Intelligence)

K.L.E. Technological University, Hubli

Repository Structure
text
PGC-Experiment-5-Neural-Network-Layers-in-CUDA/
│
├── README.md
│
├── neural_network.cu
│
├── graphs/
│   ├── 01_cpu_gpu_execution_comparison.png
│   ├── 02_gpu_speedup_comparison.png
│   └── 03_execution_time_comparison.png
│
├── results/
│   ├── neural_network_output.txt
│   ├── performance_results.txt
│   └── validation_results.txt
│
└── screenshots/
    ├── 01_gpu_detection.png
    ├── 02_cuda_compilation.png
    ├── 03_kernel_tests.png
    ├── 04_cpu_gpu_execution.png
    └── 05_performance_comparison.png


Note: Graphs, result files, and screenshots should be added after generating and saving your actual experiment outputs.
