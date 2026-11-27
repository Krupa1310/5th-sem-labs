"""
Experiment 7: Profiling and GPU Utilization

Baseline:
    Pageable host memory, default stream, blocking copies.

Optimized:
    Pinned host memory, two CUDA streams, and double buffering to
    overlap copying batch i+1 with computation on batch i.

Examples:
    python gpu_workload.py --mode baseline --profile
    python gpu_workload.py --mode optimized --profile
"""

import argparse
import math
import time

import torch


def make_weights(n):
    """Create a reproducible square weight matrix on the GPU."""
    generator = torch.Generator().manual_seed(1)
    return (torch.randn(n, n, generator=generator) / math.sqrt(n)).cuda()


def make_host_batches(rows, cols, pinned, unique=4):
    """Create reusable host batches, optionally using pinned memory."""
    generator = torch.Generator().manual_seed(0)
    batches = []

    for _ in range(unique):
        tensor = torch.randn(rows, cols, generator=generator)
        batches.append(tensor.pin_memory() if pinned else tensor)

    return batches


def compute(x, weights, reps):
    """Perform GEMM, element-wise operations, and row-wise reduction."""
    y = x
    for _ in range(reps):
        y = y @ weights
        y = torch.relu(y)
        y = y.mul(0.5).add(1.0)

    return y.sum(dim=1)


def run_baseline(host, weights, reps, nbatches):
    """Run sequential blocking copies and computation."""
    results = []

    for i in range(nbatches):
        x = host[i % len(host)].cuda()
        result = compute(x, weights, reps)
        results.append(result.cpu())
        torch.cuda.synchronize()

    return torch.stack(results)


def run_optimized(host, weights, reps, nbatches):
    """Overlap asynchronous host-to-device copies and GPU computation."""
    rows, cols = host[0].shape

    copy_stream = torch.cuda.Stream()
    compute_stream = torch.cuda.Stream()

    # Two GPU buffers implement double buffering.
    buffers = [
        torch.empty(rows, cols, device="cuda"),
        torch.empty(rows, cols, device="cuda"),
    ]

    copied = [torch.cuda.Event() for _ in range(2)]
    freed = [torch.cuda.Event() for _ in range(2)]

    # The output is pinned so asynchronous device-to-host copies are possible.
    output_host = torch.empty(nbatches, rows, pin_memory=True)

    torch.cuda.synchronize()

    # Initially, both buffers are free to receive data.
    for event in freed:
        event.record(compute_stream)

    def issue_copy(batch_index):
        buffer_index = batch_index % 2

        # Do not overwrite a buffer until its previous computation is complete.
        copy_stream.wait_event(freed[buffer_index])

        with torch.cuda.stream(copy_stream):
            buffers[buffer_index].copy_(
                host[batch_index % len(host)],
                non_blocking=True,
            )
            copied[buffer_index].record(copy_stream)

    if nbatches == 0:
        return output_host

    issue_copy(0)

    for i in range(nbatches):
        buffer_index = i % 2

        # Prefetch the next batch while the current batch is being processed.
        if i + 1 < nbatches:
            issue_copy(i + 1)

        # Computation must wait until this batch's copy has completed.
        compute_stream.wait_event(copied[buffer_index])

        with torch.cuda.stream(compute_stream):
            result = compute(buffers[buffer_index], weights, reps)

            # The buffer can be reused after its computation has finished.
            freed[buffer_index].record(compute_stream)

            # Queue asynchronous device-to-host output transfer.
            output_host[i].copy_(result, non_blocking=True)

    torch.cuda.synchronize()
    return output_host


def main():
    parser = argparse.ArgumentParser(
        description="Profile baseline and optimized GPU workloads."
    )
    parser.add_argument(
        "--mode",
        choices=["baseline", "optimized"],
        required=True,
    )
    parser.add_argument("--batches", type=int, default=200)
    parser.add_argument("--rows", type=int, default=16384)
    parser.add_argument("--cols", type=int, default=1024)
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--profile-batches", type=int, default=10)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise SystemExit(
            "CUDA GPU not available - check the NVIDIA driver and "
            "CUDA-enabled PyTorch installation."
        )

    if args.batches <= 0 or args.profile_batches <= 0:
        raise SystemExit("--batches and --profile-batches must be positive.")
    if args.rows <= 0 or args.cols <= 0 or args.reps <= 0:
        raise SystemExit("--rows, --cols, and --reps must be positive.")

    pinned = args.mode == "optimized"
    workload = run_optimized if pinned else run_baseline

    host = make_host_batches(args.rows, args.cols, pinned)
    weights = make_weights(args.cols)

    print(f"GPU          : {torch.cuda.get_device_name(0)}")
    print(f"Mode         : {args.mode}")
    print(f"Batch size   : {args.rows * args.cols * 4 / 1e6:.0f} MB")

    # Warm-up initializes CUDA, cuBLAS, and the memory allocator.
    workload(host, weights, args.reps, 3)
    torch.cuda.synchronize()

    start_time = time.perf_counter()
    results = workload(host, weights, args.reps, args.batches)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start_time

    print(f"Batches      : {args.batches}")
    print(f"Total time   : {elapsed:.3f} s")
    print(f"Per batch    : {elapsed / args.batches * 1000:.2f} ms")
    print(f"Throughput   : {args.batches / elapsed:.1f} batches/s")
    print(f"Checksum     : {results.double().sum().item():.6e}")

    if args.profile:
        from torch.profiler import ProfilerActivity, profile

        with profile(
            activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]
        ) as profiler:
            workload(host, weights, args.reps, args.profile_batches)

        torch.cuda.synchronize()

        trace_name = f"trace_{args.mode}.json"
        profiler.export_chrome_trace(trace_name)
        print(f"\nTrace saved: {trace_name}")

        for sort_key in ("cuda_time_total", "device_time_total"):
            try:
                print(
                    profiler.key_averages().table(
                        sort_by=sort_key,
                        row_limit=10,
                    )
                )
                break
            except Exception:
                continue


if __name__ == "__main__":
    main()
