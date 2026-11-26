
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

int main(int argc, char **argv) {
    size_t mb = argc > 1 ? atol(argv[1]) : 512;
    size_t n = mb << 20;

    char *buf = malloc(n);

    if (buf == NULL) {
        printf("Memory allocation failed\n");
        return 1;
    }

    /* Initialize memory using first-touch allocation */
    for (size_t i = 0; i < n; i++) {
        buf[i] = 1;
    }

    long long sum = 0;

    double t0 = omp_get_wtime();

    for (int pass = 0; pass < 4; pass++) {
        #pragma omp parallel for reduction(+:sum)
        for (size_t i = 0; i < n; i += 64) {
            sum += buf[i];
        }
    }

    double elapsed = omp_get_wtime() - t0;

    printf("buffer=%zu MB | threads=%d | sum=%lld | time=%.4f s\n",
           mb, omp_get_max_threads(), sum, elapsed);

    free(buf);

    return 0;
}


