PGC Experiment 5: Neural Network Layers in CUDA
Aim

To implement and evaluate basic neural network layers using custom CUDA kernels.

Technologies Used
CUDA Toolkit 13.4
C++
Visual Studio 2022
NVIDIA GeForce RTX 5060 Ti
Implemented Operations
Matrix multiplication with bias
ReLU activation
Sigmoid activation
CPU and GPU forward pass
Execution time and speedup calculation
Network Configuration
Batch size: 256
Input size: 128
Hidden size: 64
Output size: 10
Repeats: 20
Experimental Results
Measurement	Result
CPU time	0.686005 ms
GPU kernel-only time	0.024141 ms
GPU end-to-end time	0.121150 ms
Kernel-only speedup	28.416828x
End-to-end speedup	5.662443x
Maximum absolute difference	0.000000
Validation
Matrix multiplication with bias: PASSED
ReLU: PASSED
Sigmoid: PASSED
CPU/GPU output: MATCH
GPU

NVIDIA GeForce RTX 5060 Ti

Compilation
cmd
nvcc -O2 -arch=sm_120 neural_network.cu -o neural_network.exe

Execution
cmd
neural_network.exe

Conclusion

Neural network layers were successfully implemented using custom CUDA kernels. All kernel tests passed, and CPU and GPU outputs matched within the specified tolerance. GPU acceleration achieved a kernel-only speedup of approximately 28.42x.