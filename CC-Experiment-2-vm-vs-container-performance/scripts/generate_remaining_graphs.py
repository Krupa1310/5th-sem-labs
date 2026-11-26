import os
import re
import csv
import matplotlib.pyplot as plt

FIG = "results/figures"
RAW = "results/raw"
os.makedirs(FIG, exist_ok=True)

# ---------------- Memory ----------------
def read_memory_file(path):
    values = []
    with open(path) as f:
        for line in f:
            m = re.search(r'([\d.]+)\s+MiB/sec', line)
            if m:
                values.append(float(m.group(1)))
    return values

vm_mem = read_memory_file(f"{RAW}/memory_vm_recovered.txt")
container_mem = read_memory_file(f"{RAW}/memory_container_recovered.txt")

if vm_mem and container_mem:
    plt.figure(figsize=(8, 5))
    plt.boxplot([vm_mem, container_mem], labels=["VM", "Container"])
    plt.ylabel("Memory Throughput (MiB/sec)")
    plt.title("Memory Performance: VM vs Container")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{FIG}/memory_performance.png", dpi=200)
    plt.close()

# ---------------- Disk ----------------
def read_bw(path):
    with open(path) as f:
        text = f.read()
    m = re.search(r'BW[=\s]+([\d.]+)([KMG]iB/s)', text)
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2)
    if unit == "KiB/s":
        value /= 1024
    elif unit == "GiB/s":
        value *= 1024
    return value

disk_data = [
    ("Sequential Read", "VM", read_bw(f"{RAW}/disk-vm-seqread.txt")),
    ("Sequential Read", "Container", read_bw(f"{RAW}/disk/seq-read.txt")),
    ("Sequential Write", "VM", read_bw(f"{RAW}/disk-vm-seqwrite.txt")),
    ("Sequential Write", "Container", read_bw(f"{RAW}/disk/seq-write.txt")),
]

labels = []
vm_values = []
container_values = []

for metric, system, value in disk_data:
    if metric not in labels:
        labels.append(metric)
        vm_values.append(None)
        container_values.append(None)
    i = labels.index(metric)
    if system == "VM":
        vm_values[i] = value
    else:
        container_values[i] = value

x = range(len(labels))
width = 0.35

plt.figure(figsize=(9, 5))
plt.bar([i - width/2 for i in x], vm_values, width, label="VM")
plt.bar([i + width/2 for i in x], container_values, width, label="Container")
plt.xticks(list(x), labels)
plt.ylabel("Throughput (MiB/s)")
plt.title("Disk Performance: VM vs Container")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{FIG}/disk_performance.png", dpi=200)
plt.close()

# ---------------- Network ----------------
path = f"{RAW}/network/iperf3.txt"
intervals = []
throughput = []

with open(path) as f:
    for line in f:
        m = re.search(
            r'\s(\d+(?:\.\d+)?)-\s*(\d+(?:\.\d+)?)\s+sec\s+.*?\s([\d.]+)\s+Gbits/sec',
            line
        )
        if m:
            intervals.append(f"{m.group(1)}-{m.group(2)}")
            throughput.append(float(m.group(3)))

if throughput:
    plt.figure(figsize=(9, 5))
    plt.plot(intervals, throughput, marker="o")
    plt.xlabel("Time Interval (sec)")
    plt.ylabel("Throughput (Gbits/sec)")
    plt.title("Network Throughput")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{FIG}/network_performance.png", dpi=200)
    plt.close()

# ---------------- Application + Startup ----------------
csv_path = "results/processed/final_comparison.csv"

rows = []
with open(csv_path, newline="") as f:
    rows = list(csv.DictReader(f))

app_rows = [r for r in rows if r["Metric"].startswith("API Requests/sec")]

if app_rows:
    labels = ["Health", "Compute"]
    vm = [float(app_rows[0]["VM"]), float(app_rows[1]["VM"])]
    container = [float(app_rows[0]["Container"]), float(app_rows[1]["Container"])]

    x = range(len(labels))

    plt.figure(figsize=(8, 5))
    plt.bar([i - width/2 for i in x], vm, width, label="VM")
    plt.bar([i + width/2 for i in x], container, width, label="Container")
    plt.xticks(list(x), labels)
    plt.ylabel("Requests/sec")
    plt.title("Application Performance: API Requests/sec")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{FIG}/application_performance.png", dpi=200)
    plt.close()

lat_rows = [r for r in rows if r["Metric"].startswith("API Latency")]

if lat_rows:
    labels = ["Health", "Compute"]
    vm = [float(lat_rows[0]["VM"]), float(lat_rows[1]["VM"])]
    container = [float(lat_rows[0]["Container"]), float(lat_rows[1]["Container"])]

    x = range(len(labels))

    plt.figure(figsize=(8, 5))
    plt.bar([i - width/2 for i in x], vm, width, label="VM")
    plt.bar([i + width/2 for i in x], container, width, label="Container")
    plt.xticks(list(x), labels)
    plt.ylabel("Latency (ms)")
    plt.title("Application Latency: VM vs Container")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{FIG}/application_latency.png", dpi=200)
    plt.close()

startup = next((r for r in rows if r["Metric"] == "Startup Time"), None)

if startup and startup["Container"] != "N/A":
    plt.figure(figsize=(6, 5))
    plt.bar(["Container"], [float(startup["Container"])])
    plt.ylabel("Startup Time (seconds)")
    plt.title("Container Startup Time")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{FIG}/startup_time.png", dpi=200)
    plt.close()

print("Remaining graphs generated successfully.")
