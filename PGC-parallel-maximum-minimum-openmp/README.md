# Parallel Maximum/Minimum Search using OpenMP

## 1. Problem Definition

The objective of this experiment is to find the maximum and minimum values from a large dataset using parallel processing with OpenMP.

The experiment compares sequential and parallel execution and analyzes execution time, speedup, and efficiency for different numbers of threads.

## 2. Objectives

- Find the maximum value in a large dataset.
- Find the minimum value in a large dataset.
- Implement the sequential algorithm.
- Implement the parallel algorithm using OpenMP.
- Execute the program using different numbers of threads.
- Test the program with different data sizes.
- Calculate speedup and efficiency.
- Generate graphs and analyze the results.

## 3. Tools and Technologies

- Operating System: Ubuntu on WSL2
- Programming Language: C
- Compiler: GCC
- Parallel Programming Model: OpenMP
- Graph Generation: Python
- Graph Library: Matplotlib
- Version Control: Git
- GitHub

## 4. Sequential Algorithm

1. Generate the dataset.
2. Initialize minimum to INT_MAX.
3. Initialize maximum to INT_MIN.
4. Traverse every element of the dataset.
5. If an element is smaller than minimum, update minimum.
6. If an element is larger than maximum, update maximum.
7. Display the minimum and maximum values.

## 5. Parallel Design

OpenMP is used to divide the search operation among multiple threads.

The loop is parallelized using:

    #pragma omp parallel for reduction(min:minimum) reduction(max:maximum)

The reduction clauses allow each thread to calculate local minimum and maximum values and combine them into the final minimum and maximum values.

## 6. Dataset

The program generates integer values between 1 and 1,000,000.

A fixed random seed of 42 is used so that the same dataset can be generated consistently.

## 7. Thread Scaling Results

| Threads | Data Size | Execution Time (s) |
|--------:|----------:|-------------------:|
| 1 | 10,000,000 | 0.007940 |
| 2 | 10,000,000 | 0.007246 |
| 4 | 10,000,000 | 0.007538 |
| 8 | 10,000,000 | 0.005069 |

## 8. Data Size Results

| Data Size | Threads | Minimum | Maximum | Execution Time (s) |
|----------:|--------:|--------:|--------:|-------------------:|
| 1,000,000 | 8 | 1 | 1,000,000 | 0.001475 |
| 5,000,000 | 8 | 1 | 1,000,000 | 0.003315 |
| 10,000,000 | 8 | 1 | 1,000,000 | 0.008019 |

## 9. Speedup and Efficiency

The sequential execution time for 10,000,000 elements was 0.004681 seconds.

Speedup is calculated as:

    Speedup = Sequential Time / Parallel Time

Efficiency is calculated as:

    Efficiency = Speedup / Number of Threads × 100

| Threads | Sequential Time (s) | Parallel Time (s) | Speedup | Efficiency (%) |
|--------:|--------------------:|------------------:|--------:|---------------:|
| 1 | 0.004681 | 0.007940 | 0.5895 | 58.95 |
| 2 | 0.004681 | 0.007246 | 0.6460 | 32.30 |
| 4 | 0.004681 | 0.007538 | 0.6210 | 15.52 |
| 8 | 0.004681 | 0.005069 | 0.9235 | 11.54 |

## 10. Result Analysis

The execution time was measured using 1, 2, 4 and 8 OpenMP threads.

The lowest measured parallel execution time was obtained with 8 threads.

The speedup is below 1 for the tested configurations because the sequential maximum/minimum search is a very small computation and OpenMP introduces overhead such as thread management, scheduling and reduction overhead.

The data-size experiment shows that execution time increases as the dataset size increases because every element must be examined.

The experiment demonstrates that parallel performance depends on both the amount of computation and the overhead introduced by parallel execution.

## 11. Graphs

### Execution Time vs Number of Threads

![Execution Time vs Threads](graphs/execution_time_vs_threads.png)

### Speedup vs Number of Threads

![Speedup vs Threads](graphs/speedup_vs_threads.png)

### Execution Time vs Data Size

![Execution Time vs Data Size](graphs/execution_time_vs_data_size.png)

## 12. Project Structure

    parallel-maximum-minimum-openmp/
    |
    |-- README.md
    |-- generate_graphs.py
    |
    |-- src/
    |   |-- sequential_maxmin.c
    |   `-- maxmin_openmp.c
    |
    |-- data/
    |
    |-- results/
    |   |-- thread_results.csv
    |   |-- data_size_results.csv
    |   |-- speedup_efficiency.csv
    |   `-- analysis.txt
    |
    |-- graphs/
    |   |-- execution_time_vs_threads.png
    |   |-- speedup_vs_threads.png
    |   `-- execution_time_vs_data_size.png
    |
    `-- presentation/

## 13. Conclusion

The experiment successfully implements maximum and minimum search using OpenMP parallel reduction.

The program was tested with different numbers of threads and different dataset sizes. Execution time, speedup and efficiency were calculated and visualized using graphs.

The experiment demonstrates the effect of parallelization overhead and dataset size on OpenMP performance.

