
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("graphs", exist_ok=True)

# -------------------------------------------------
# GRAPH 1: Cache coherence bus transactions
# -------------------------------------------------

protocols = ["MSI", "MESI", "MOESI"]

adjacent = [4000, 3999, 3999]
padded = [4, 2, 2]

x = np.arange(len(protocols))
width = 0.35

plt.figure(figsize=(9, 5))

plt.bar(x - width / 2, adjacent, width, label="Adjacent")
plt.bar(x + width / 2, padded, width, label="Padded")

plt.xlabel("Cache Coherence Protocol")
plt.ylabel("Bus Transactions")
plt.title("MSI, MESI and MOESI Bus Transaction Comparison")
plt.xticks(x, protocols)
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("graphs/01_cache_coherence_comparison.png", dpi=300)
plt.close()


# -------------------------------------------------
# GRAPH 2: False sharing performance
# -------------------------------------------------

threads = [1, 2, 4]

adjacent_time = [0.1840, 0.1716, 0.1853]
padded_time = [0.1837, 0.0908, 0.0504]

x = np.arange(len(threads))

plt.figure(figsize=(9, 5))

plt.plot(threads, adjacent_time, marker="o",
         linewidth=2, label="Adjacent")

plt.plot(threads, padded_time, marker="s",
         linewidth=2, label="Padded")

plt.xlabel("Number of Threads")
plt.ylabel("Execution Time (seconds)")
plt.title("False Sharing: Adjacent vs Padded")
plt.xticks(threads)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("graphs/02_false_sharing_performance.png", dpi=300)
plt.close()


# -------------------------------------------------
# GRAPH 3: NUMA memory sweep performance
# -------------------------------------------------

threads = [1, 2, 4]
memory_time = [0.1798, 0.1395, 0.1058]

plt.figure(figsize=(9, 5))

plt.plot(threads, memory_time, marker="o",
         linewidth=2)

plt.xlabel("Number of Threads")
plt.ylabel("Execution Time (seconds)")
plt.title("NUMA Memory Sweep Performance (512 MB)")
plt.xticks(threads)
plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("graphs/03_numa_memory_performance.png", dpi=300)
plt.close()


print("All graphs generated successfully!")
print("1. graphs/01_cache_coherence_comparison.png")
print("2. graphs/02_false_sharing_performance.png")
print("3. graphs/03_numa_memory_performance.png")



