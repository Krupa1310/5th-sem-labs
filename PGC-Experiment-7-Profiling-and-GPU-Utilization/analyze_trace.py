"""
Experiment 7: Analyze PyTorch profiler Chrome trace files.

Usage:
    python analyze_trace.py trace_baseline.json
    python analyze_trace.py trace_baseline.json trace_optimized.json
"""

import collections
import json
import sys

GAP_US = 50
COMPUTE_HINTS = ("gemm", "sgemm", "cutlass", "cublas", "conv", "wmma")


def merge_intervals(intervals):
    """Merge overlapping time intervals."""
    intervals = sorted(intervals)
    merged = []

    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged


def total_time(intervals):
    return sum(end - start for start, end in intervals)


def overlap_time(first, second):
    """Calculate the overlap between two sorted interval lists."""
    i = j = overlap = 0

    while i < len(first) and j < len(second):
        start = max(first[i][0], second[j][0])
        end = min(first[i][1], second[j][1])

        if end > start:
            overlap += end - start

        if first[i][1] < second[j][1]:
            i += 1
        else:
            j += 1

    return overlap


def classify_kernel(name):
    """Apply the lab manual's name-based classification hint."""
    lower_name = name.lower()
    if any(hint in lower_name for hint in COMPUTE_HINTS):
        return "compute-bound"
    return "memory-bound"


def analyze(path):
    with open(path, encoding="utf-8") as trace_file:
        data = json.load(trace_file)

    events = data["traceEvents"] if isinstance(data, dict) else data

    kernels = []
    copies = []
    kernel_names = collections.defaultdict(lambda: [0, 0.0])
    copy_names = collections.defaultdict(lambda: [0, 0.0])

    for event in events:
        if event.get("ph") != "X":
            continue

        category = event.get("cat", "")
        start = event.get("ts", 0)
        duration = event.get("dur", 0)
        name = event.get("name", "unknown")

        if category == "kernel":
            kernels.append([start, start + duration])
            kernel_names[name[:60]][0] += 1
            kernel_names[name[:60]][1] += duration
        elif category in ("gpu_memcpy", "gpu_memset"):
            copies.append([start, start + duration])
            copy_names[name[:60]][0] += 1
            copy_names[name[:60]][1] += duration

    if not kernels:
        print(f"{path}: no GPU kernels found in trace")
        return None

    merged_kernels = merge_intervals(kernels)
    merged_copies = merge_intervals(copies)

    all_intervals = merged_kernels + merged_copies
    start_time = min(interval[0] for interval in all_intervals)
    end_time = max(interval[1] for interval in all_intervals)
    window = end_time - start_time

    if window <= 0:
        print(f"{path}: invalid or empty profiled time window")
        return None

    kernel_busy = total_time(merged_kernels)
    gaps = [
        merged_kernels[i + 1][0] - merged_kernels[i][1]
        for i in range(len(merged_kernels) - 1)
    ]
    large_gaps = [gap for gap in gaps if gap > GAP_US]
    copy_busy = total_time(merged_copies)
    copy_overlap = overlap_time(merged_kernels, merged_copies)

    print("=" * 72)
    print(path)
    print("=" * 72)
    print(f"Profiled window             : {window / 1000:9.2f} ms")
    print(f"Kernel busy time            : {kernel_busy / 1000:9.2f} ms")
    print(f"GPU utilization (busy/window): {100 * kernel_busy / window:8.1f} %")
    print(f"Copy busy time              : {copy_busy / 1000:9.2f} ms")
    print(f"Copy overlapped with kernels: {copy_overlap / 1000:9.2f} ms")
    print(
        f"Idle gaps > {GAP_US} us          : {len(large_gaps):9d} "
        f"(total {sum(large_gaps) / 1000:.2f} ms)"
    )

    print("\nKernels (name-based classification hint)")
    print(f"{'calls':>6} {'total ms':>10} {'label':<14} name")
    for name, (count, duration) in sorted(
        kernel_names.items(), key=lambda item: -item[1][1]
    ):
        print(
            f"{count:6d} {duration / 1000:10.2f} "
            f"{classify_kernel(name):<14} {name}"
        )

    print("\nMemory copies")
    print(f"{'calls':>6} {'total ms':>10} name")
    for name, (count, duration) in sorted(
        copy_names.items(), key=lambda item: -item[1][1]
    ):
        print(f"{count:6d} {duration / 1000:10.2f} {name}")

    print()
    return window, kernel_busy, copy_busy, copy_overlap, len(large_gaps)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python analyze_trace.py trace_baseline.json "
            "[trace_optimized.json ...]"
        )

    rows = []
    for path in sys.argv[1:]:
        result = analyze(path)
        if result:
            rows.append((path, result))

    if len(rows) > 1:
        print("SUMMARY")
        print(
            f"{'file':<28}{'window ms':>12}{'util %':>10}"
            f"{'overlap ms':>13}{'gaps':>8}"
        )
        for path, (window, busy, _, overlap, gaps) in rows:
            print(
                f"{path:<28}{window / 1000:12.1f}"
                f"{100 * busy / window:10.1f}"
                f"{overlap / 1000:13.1f}{gaps:8d}"
            )


if __name__ == "__main__":
    main()
