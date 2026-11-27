# 2D Convolution and Image Filtering Using CUDA

## Project Overview
This project implements 2D image convolution using CPU and NVIDIA CUDA GPU computing. It compares three GPU implementations to study the performance benefits of different CUDA memory optimization techniques.

## Hardware and Software
- GPU: NVIDIA GeForce RTX 5060 Ti (16 GB)
- CUDA Toolkit: 13.4
- C++ and CUDA C++
- Python 3.12
- NumPy and Pillow
- Matplotlib
- Microsoft Visual Studio Build Tools

## Input Image
- Image dimensions: 2048 x 2048
- Image type: Grayscale
- Filter sizes: 3x3, 5x5 and 7x7

## Implementations

### 1. CPU Reference
A sequential C++ implementation used as the reference for correctness validation.

### 2. Naive CUDA
Each CUDA thread calculates one output pixel using global memory.

### 3. Constant Memory CUDA
Uses CUDA constant memory to store convolution filter coefficients.

### 4. Shared Memory CUDA
Uses shared memory to load image tiles and neighboring halo pixels, reducing repeated global memory accesses.

## Correctness Validation
All three GPU implementations were compared against the CPU reference for all three filter sizes.

- Total comparisons: 9
- Failed comparisons: 0
- Mismatched pixels: 0
- Error tolerance: 0.0002

All correctness tests passed.

## Performance Results

| Filter | CPU (ms) | Naive CUDA (ms) | Constant (ms) | Shared (ms) |
|---|---:|---:|---:|---:|
| 3x3 | 42.3285 | 0.0866 | 0.0901 | 0.0845 |
| 5x5 | 82.6065 | 0.1356 | 0.1650 | 0.1444 |
| 7x7 | 155.8290 | 0.2549 | 0.2870 | 0.1681 |

GPU timings represent average kernel execution time. CPU timings represent CPU convolution execution time; therefore, these are not end-to-end equivalent measurements.

## Project Results
The project generates:
- Filtered output images for all GPU implementations.
- CPU and GPU correctness validation results.
- GPU performance comparison graph.
- CPU versus GPU timing graph.
- Performance results in CSV format.

## How to Compile

Open a PowerShell terminal configured with the Visual Studio C++ compiler.

```powershell
cl /O2 /EHsc .\src\cpu_reference.cpp /Fe:cpu_reference.exe

nvcc -arch=sm_120 .\src\naive_convolution.cu -o .\naive_convolution.exe

nvcc -arch=sm_120 .\src\constant_memory.cu -o .\constant_memory.exe

nvcc -arch=sm_120 .\src\shared_memory.cu -o .\shared_memory.exe
```

## How to Run

```powershell
.\cpu_reference.exe
.\naive_convolution.exe
.\constant_memory.exe
.\shared_memory.exe
```

Run the correctness validation:

```powershell
python .\compare_results.py
```

Generate output PNG images:

```powershell
python .\convert_outputs.py
```

Generate performance graphs and CSV:

```powershell
python .\performance_analysis.py
```

## Conclusion
This project demonstrates how CUDA parallel processing and GPU memory optimization techniques can accelerate 2D image convolution. It compares global memory, constant memory and shared memory implementations and evaluates their correctness and performance for different filter sizes.
