
import numpy as np

width = 2048
height = 2048

filters = ["3x3", "5x5", "7x7"]
tolerance = 0.0002

print("\nCPU vs GPU CORRECTNESS VALIDATION")
print("---------------------------------------------")

for mask in filters:
    cpu = np.fromfile(f"output/cpu_{mask}.raw", dtype=np.float32)
    naive = np.fromfile(f"output/naive_{mask}.raw", dtype=np.float32)
    constant = np.fromfile(f"output/constant_{mask}.raw", dtype=np.float32)
    shared = np.fromfile(f"output/shared_{mask}.raw", dtype=np.float32)

    cpu = cpu.reshape((height, width))
    naive = naive.reshape((height, width))
    constant = constant.reshape((height, width))
    shared = shared.reshape((height, width))

    naive_difference = np.abs(cpu - naive)
    constant_difference = np.abs(cpu - constant)
    shared_difference = np.abs(cpu - shared)

    naive_max_error = np.max(naive_difference)
    constant_max_error = np.max(constant_difference)
    shared_max_error = np.max(shared_difference)

    naive_mean_error = np.mean(naive_difference)
    constant_mean_error = np.mean(constant_difference)
    shared_mean_error = np.mean(shared_difference)

    naive_mismatch = np.sum(naive_difference > tolerance)
    constant_mismatch = np.sum(constant_difference > tolerance)
    shared_mismatch = np.sum(shared_difference > tolerance)

    print(f"\nFilter: {mask}")

    print("\nNaive CUDA:")
    print(f"Maximum error: {naive_max_error:.10f}")
    print(f"Mean error: {naive_mean_error:.10f}")
    print(f"Mismatched pixels: {naive_mismatch}")
    print("Result:", "PASS" if naive_max_error <= tolerance else "CHECK REQUIRED")

    print("\nConstant Memory CUDA:")
    print(f"Maximum error: {constant_max_error:.10f}")
    print(f"Mean error: {constant_mean_error:.10f}")
    print(f"Mismatched pixels: {constant_mismatch}")
    print("Result:", "PASS" if constant_max_error <= tolerance else "CHECK REQUIRED")

    print("\nShared Memory CUDA:")
    print(f"Maximum error: {shared_max_error:.10f}")
    print(f"Mean error: {shared_mean_error:.10f}")
    print(f"Mismatched pixels: {shared_mismatch}")
    print("Result:", "PASS" if shared_max_error <= tolerance else "CHECK REQUIRED")

print("\nAll correctness validations completed!")
