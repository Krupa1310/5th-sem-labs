Experiment 6: Memory Optimization in CUDA
Aim

To study how global-memory access patterns affect CUDA performance using uncoalesced transpose, coalesced transpose and naive matrix multiplication.

Hardware and Software
GPU: NVIDIA GeForce RTX 5060 Ti
Compute Capability: 12.0
CUDA Toolkit: 13.4
Compiler: NVCC
OS: Windows
Experimental Results
Kernel	Average Time (ms)	Performance
Uncoalesced Transpose	0.793	169.3 GB/s
Coalesced Transpose	0.418	320.7 GB/s
Naive Matrix Multiplication	1.439	1492.4 GFLOPS
Transpose Speedup

Approximately 1.90x.

Verification

All three kernels passed verification in all three runs.

Conclusion

Coalesced global-memory access using shared memory improved transpose performance by approximately 1.90x compared with uncoalesced access. The experiment demonstrated the importance of memory coalescing and efficient GPU memory utilization.