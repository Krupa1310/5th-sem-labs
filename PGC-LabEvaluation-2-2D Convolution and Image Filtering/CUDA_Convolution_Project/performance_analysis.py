
import csv
import os
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)

filters = ["3x3", "5x5", "7x7"]

cpu_times = [42.3285, 82.6065, 155.829]

naive_times = [0.0866, 0.1356, 0.2549]

constant_times = [0.0901328, 0.165018, 0.287]

shared_times = [0.0845232, 0.14443, 0.168134]

print("\nCUDA IMAGE CONVOLUTION PERFORMANCE ANALYSIS")
print("=" * 65)

rows = []

for i, mask in enumerate(filters):

    naive_speedup = naive_times[i] / naive_times[i]
    constant_speedup = naive_times[i] / constant_times[i]
    shared_speedup = naive_times[i] / shared_times[i]

    cpu_naive_ratio = cpu_times[i] / naive_times[i]
    cpu_constant_ratio = cpu_times[i] / constant_times[i]
    cpu_shared_ratio = cpu_times[i] / shared_times[i]

    print(f"\nFilter: {mask}")
    print("-" * 45)

    print(f"CPU Time:              {cpu_times[i]:.6f} ms")
    print(f"Naive CUDA Time:       {naive_times[i]:.6f} ms")
    print(f"Constant Memory Time:  {constant_times[i]:.6f} ms")
    print(f"Shared Memory Time:    {shared_times[i]:.6f} ms")

    print("\nGPU Relative Performance:")

    print(f"Naive CUDA:       {naive_speedup:.4f}x")
    print(f"Constant Memory:  {constant_speedup:.4f}x")
    print(f"Shared Memory:    {shared_speedup:.4f}x")

    print("\nCPU Time / GPU Kernel Time Ratios:")
    print(f"Naive CUDA:       {cpu_naive_ratio:.2f}x")
    print(f"Constant Memory:  {cpu_constant_ratio:.2f}x")
    print(f"Shared Memory:    {cpu_shared_ratio:.2f}x")

    rows.append([
        mask,
        cpu_times[i],
        naive_times[i],
        constant_times[i],
        shared_times[i],
        naive_speedup,
        constant_speedup,
        shared_speedup,
        cpu_naive_ratio,
        cpu_constant_ratio,
        cpu_shared_ratio
    ])

csv_file = "results/performance_results.csv"

with open(csv_file, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Filter",
        "CPU Time (ms)",
        "Naive CUDA (ms)",
        "Constant Memory (ms)",
        "Shared Memory (ms)",
        "Naive Relative Speedup",
        "Constant Relative Speedup",
        "Shared Relative Speedup",
        "CPU/Naive Kernel-Time Ratio",
        "CPU/Constant Kernel-Time Ratio",
        "CPU/Shared Kernel-Time Ratio"
    ])

    writer.writerows(rows)

print("\nCSV saved:", csv_file)

x = range(len(filters))
bar_width = 0.25

plt.figure(figsize=(10, 6))

plt.bar(
    [i - bar_width for i in x],
    naive_times,
    width=bar_width,
    label="Naive CUDA"
)

plt.bar(
    x,
    constant_times,
    width=bar_width,
    label="Constant Memory"
)

plt.bar(
    [i + bar_width for i in x],
    shared_times,
    width=bar_width,
    label="Shared Memory"
)

plt.xlabel("Filter Size")
plt.ylabel("Average Execution Time (ms)")
plt.title("GPU Convolution Performance Comparison")
plt.xticks(list(x), filters)
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("results/gpu_performance_comparison.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 6))

plt.bar(
    [i - bar_width for i in x],
    cpu_times,
    width=bar_width,
    label="CPU"
)

plt.bar(
    x,
    naive_times,
    width=bar_width,
    label="Naive CUDA Kernel"
)

plt.bar(
    [i + bar_width for i in x],
    shared_times,
    width=bar_width,
    label="Shared Memory CUDA Kernel"
)

plt.xlabel("Filter Size")
plt.ylabel("Execution Time (ms)")
plt.title("CPU vs GPU Convolution Timing")
plt.xticks(list(x), filters)
plt.yscale("log")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("results/cpu_gpu_comparison.png", dpi=300)
plt.close()

print("\nGRAPHS GENERATED SUCCESSFULLY")
print("--------------------------------")
print("1. results/gpu_performance_comparison.png")
print("2. results/cpu_gpu_comparison.png")

print("\nPERFORMANCE ANALYSIS COMPLETED!")
