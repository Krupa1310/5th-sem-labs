
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define N 100000000L

void run_false_sharing(int nt, int padded) {
    int stride = padded ? 8 : 1;

    size_t bytes =
        ((size_t)nt * stride * sizeof(long) + 63) / 64 * 64;

    long *cnt = aligned_alloc(64, bytes);

    if (cnt == NULL) {
        printf("Memory allocation failed\n");
        return;
    }

    for (int i = 0; i < nt * stride; i++) {
        cnt[i] = 0;
    }

    omp_set_num_threads(nt);

    double start = omp_get_wtime();

    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        volatile long *p = &cnt[tid * stride];

        for (long i = 0; i < N / nt; i++) {
            (*p)++;
        }
    }

    double elapsed = omp_get_wtime() - start;

    long total = 0;

    for (int i = 0; i < nt; i++) {
        total += cnt[i * stride];
    }

    printf("%-10s | threads=%d | total=%ld | time=%.4f s\n",
           padded ? "padded" : "adjacent",
           nt, total, elapsed);

    free(cnt);
}


void run_memory_sweep(int nt, size_t mb) {
    size_t n = mb * 1024 * 1024;

    char *buf = malloc(n);

    if (buf == NULL) {
        printf("Memory allocation failed\n");
        return;
    }

    for (size_t i = 0; i < n; i++) {
        buf[i] = 1;
    }

    long long sum = 0;

    omp_set_num_threads(nt);

    double start = omp_get_wtime();

    for (int pass = 0; pass < 4; pass++) {
        #pragma omp parallel for reduction(+:sum)
        for (size_t i = 0; i < n; i += 64) {
            sum += buf[i];
        }
    }

    double elapsed = omp_get_wtime() - start;

    printf("Memory sweep | buffer=%zu MB | threads=%d | "
           "sum=%lld | time=%.4f s\n",
           mb, nt, sum, elapsed);

    free(buf);
}


int main() {
    int thread_counts[] = {1, 2, 4};

    printf("CACHE FALSE SHARING COMPARISON\n");
    printf("---------------------------------------------\n");

    for (int i = 0; i < 3; i++) {
        int nt = thread_counts[i];

        run_false_sharing(nt, 0);
        run_false_sharing(nt, 1);

        printf("\n");
    }

    printf("\nNUMA MEMORY SWEEP COMPARISON\n");
    printf("---------------------------------------------\n");

    run_memory_sweep(1, 512);
    run_memory_sweep(2, 512);
    run_memory_sweep(4, 512);

    return 0;
}


