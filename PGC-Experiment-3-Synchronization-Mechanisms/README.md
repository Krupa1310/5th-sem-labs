# Analyze Synchronization Mechanisms in Parallel Programs

A Parallel Computing laboratory experiment implementing and analyzing different synchronization mechanisms in shared-memory parallel programs using C, OpenMP, POSIX Threads, and semaphores.

The experiment demonstrates how race conditions occur when multiple threads access shared data without synchronization and compares the correctness and execution time of Critical Sections, Atomic Operations, Locks, Barriers, and Semaphores.

The performance comparison evaluates None, Critical, Atomic, and Lock mechanisms using 1, 2, 4, and 8 threads.

## Table of Contents

1. Problem Statement
2. Objectives
3. Components and Configuration
4. Theory of Synchronization
5. System Architecture
6. Synchronization Mechanisms
7. Part A - Race Condition
8. Part B - Critical Section
9. Part C - Atomic Operation
10. Part D - Barrier Synchronization
11. Part E - Semaphore Synchronization
12. Part F - Performance Comparison
13. Execution Steps
14. Results
15. Performance Analysis
16. Troubleshooting
17. Conclusion
18. Author

---

## 1. Problem Statement

In shared-memory parallel programming, multiple threads may access and modify the same shared variable simultaneously.

When multiple threads execute operations such as `counter++` without synchronization, their operations may overlap, resulting in lost updates and incorrect output. This problem is known as a race condition.

This experiment implements different synchronization mechanisms to control concurrent access to shared resources.

The following mechanisms are studied:

- Unsynchronized shared-variable updates
- OpenMP Critical Sections
- OpenMP Atomic Operations
- OpenMP Barriers
- POSIX Binary Semaphores
- OpenMP Locks

The experiment evaluates correctness, execution time, and scalability as the number of threads increases.

## 2. Objectives

The objectives of this experiment are:

- To understand race conditions in shared-memory parallel programs.
- To implement unsynchronized shared-variable updates.
- To use OpenMP Critical Sections to protect shared data.
- To implement Atomic Operations for safe counter updates.
- To understand thread synchronization using barriers.
- To implement mutual exclusion using POSIX Semaphores.
- To understand OpenMP Locks.
- To compare execution times using different synchronization mechanisms.
- To analyze correctness and scalability with 1, 2, 4, and 8 threads.
- To identify the trade-off between synchronization overhead and performance.

## 3. Components and Configuration

### 3.1 Hardware Requirements

| Component | Configuration |
|---|---|
| Host System | Windows |
| Operating Environment | Ubuntu on WSL |
| Processor | Multi-core CPU |
| Memory | Sufficient RAM for Ubuntu and parallel execution |

### 3.2 Software Requirements

| Software / Tool | Purpose |
|---|---|
| Windows | Host operating system |
| WSL | Linux environment on Windows |
| Ubuntu | Compilation and execution environment |
| GCC Compiler | Compiles C programs |
| OpenMP | Shared-memory parallel programming |
| POSIX Threads | Thread creation and management |
| Semaphore Library | Synchronization using semaphores |
| Ubuntu Terminal | Executing programs and recording results |
| Git | Version control |
| GitHub | Source-code and experiment documentation |

## 4. Theory of Synchronization

### 4.1 Why Synchronization Is Needed

Multiple threads in a shared-memory program can access the same variable simultaneously.

For example:

`counter++`

This operation involves reading the current value, incrementing it, and writing the updated value.

If multiple threads perform these operations simultaneously, some updates may be lost.

Synchronization mechanisms coordinate access to shared resources and ensure correct program execution.

### 4.2 Race Condition

A race condition occurs when multiple threads access and modify shared data without proper synchronization.

The final result depends on the execution order and timing of the threads.

### 4.3 Critical Section

An OpenMP Critical Section uses:

`#pragma omp critical`

It allows only one thread at a time to execute the protected block.

It guarantees mutual exclusion but may introduce waiting overhead when multiple threads compete for the same resource.

### 4.4 Atomic Operation

An OpenMP Atomic Operation uses:

`#pragma omp atomic`

It ensures that a supported shared-variable operation is performed atomically.

Atomic operations are useful for simple updates and generally have less overhead than protecting an entire code block with a critical section.

### 4.5 Barrier Synchronization

An OpenMP Barrier uses:

`#pragma omp barrier`

All threads must reach the barrier before any thread can continue beyond it.

A barrier synchronizes different phases of parallel computation.

### 4.6 Semaphore

A semaphore is a synchronization mechanism used to control access to shared resources.

The POSIX functions used are:

- `sem_init()` – Initializes the semaphore.
- `sem_wait()` – Acquires the semaphore and waits if unavailable.
- `sem_post()` – Releases the semaphore.
- `sem_destroy()` – Destroys the semaphore.

A binary semaphore initialized with value 1 provides mutual exclusion.

### 4.7 OpenMP Lock

OpenMP locks provide explicit control over mutual exclusion.

The functions used are:

- `omp_init_lock()`
- `omp_set_lock()`
- `omp_unset_lock()`
- `omp_destroy_lock()`

Only one thread can hold the lock at a time.

## 5. System Architecture

The experiment uses multiple threads that access a shared counter.

### 5.1 Overall Architecture

```text
             Shared Memory
                  |
             Shared Counter
                  |
       +----------+----------+
       |          |          |
    Thread 0   Thread 1   Thread 2 ... Thread N
       |          |          |
       +----------+----------+
                  |
       Synchronization Mechanisms
                  |
    +-------------+-------------+
    |             |             |
  Critical      Atomic         Lock
    |
  Barrier and Semaphore Demonstrations
```

### 5.2 Execution Flow

```text
Windows Host
     |
     v
Ubuntu on WSL
     |
     v
GCC Compiler
     |
     v
C Programs
     |
     v
Parallel Thread Execution
     |
     v
Synchronization Mechanisms
     |
     v
Counter Verification
     |
     v
Execution Time Comparison
     |
     v
Performance Analysis
```

## 6. Synchronization Mechanisms

| Mechanism | Purpose |
|---|---|
| None | Demonstrates race conditions |
| Critical | Protects a code block |
| Atomic | Protects simple shared-variable updates |
| Barrier | Synchronizes thread execution phases |
| Semaphore | Controls access using a semaphore |
| Lock | Provides explicit mutual exclusion |

## 7. Part A - Race Condition

The first program demonstrates what happens when multiple threads update a shared counter without synchronization.

### 7.1 Source Code

File:

`race.c`

The program uses an OpenMP parallel loop to execute 10,000,000 increments.

```c
#include <stdio.h>
#include <omp.h>

int main(){
    long counter=0;

    #pragma omp parallel for
    for(long i=0;i<10000000;i++)
        counter++;

    printf("Counter=%ld\n",counter);
}
```

### 7.2 Compilation

```bash
gcc race.c -fopenmp -o race
```

### 7.3 Execution

```bash
OMP_NUM_THREADS=4 ./race
```

### 7.4 Observed Result

```text
Counter=4325508
```

Expected count:

`10000000`

The actual count is smaller because concurrent updates cause lost increments.

This demonstrates a race condition.

## 8. Part B - Critical Section

The Critical Section program protects the shared counter using OpenMP critical.

### 8.1 Source Code

File:

`critical.c`

The program uses:

`#pragma omp critical`

to ensure that only one thread updates the counter at a time.

### 8.2 Compilation

```bash
gcc critical.c -fopenmp -o critical
```

### 8.3 Execution

```bash
OMP_NUM_THREADS=4 ./critical
```

### 8.4 Observed Result

```text
Counter=10000000
```

The correct output is obtained because the critical section prevents simultaneous updates to the shared counter.

## 9. Part C - Atomic Operation

The Atomic program uses OpenMP atomic to protect the increment operation.

### 9.1 Source Code

File:

`atomic.c`

The program uses:

`#pragma omp atomic`

to perform each counter increment safely.

### 9.2 Compilation

```bash
gcc atomic.c -fopenmp -o atomic
```

### 9.3 Execution

```bash
OMP_NUM_THREADS=4 ./atomic
```

### 9.4 Observed Result

```text
Counter=10000000
```

The atomic operation ensures that every increment is performed correctly without lost updates.

## 10. Part D - Barrier Synchronization

The Barrier program demonstrates synchronization between multiple OpenMP threads.

### 10.1 Source Code

File:

`barrier.c`

The program prints a message before and after the barrier.

It uses:

`#pragma omp barrier`

All threads must reach the barrier before any thread proceeds.

### 10.2 Compilation

```bash
gcc barrier.c -fopenmp -o barrier
```

### 10.3 Execution

```bash
OMP_NUM_THREADS=4 ./barrier
```

### 10.4 Observed Result

```text
Thread 1 before barrier
Thread 2 before barrier
Thread 0 before barrier
Thread 3 before barrier
Thread 1 after barrier
Thread 0 after barrier
Thread 2 after barrier
Thread 3 after barrier
```

The order of individual thread messages may vary.

However, all messages printed before the barrier appear before any messages printed after the barrier.

This demonstrates synchronization between threads.

## 11. Part E - Semaphore Synchronization

The Semaphore program uses POSIX threads and a binary semaphore to protect a shared counter.

### 11.1 Source Code

File:

`semaphore.c`

Two threads are created using POSIX Threads.

Each thread increments the shared counter 100,000 times.

The semaphore is initialized with value 1 to provide mutual exclusion.

### 11.2 Compilation

```bash
gcc semaphore.c -pthread -o semaphore
```

### 11.3 Execution

```bash
./semaphore
```

### 11.4 Observed Result

```text
Counter=200000
```

Expected count:

`200000`

The semaphore ensures that only one thread accesses the protected counter at a time.

## 12. Part F - Performance Comparison

The comparison program evaluates four synchronization strategies:

1. None
2. Critical
3. Atomic
4. Lock

The program performs 10,000,000 increments for each mechanism.

It tests the following thread counts:

- 1 thread
- 2 threads
- 4 threads
- 8 threads

Execution time is measured using:

`omp_get_wtime()`

The final counter is also checked against the expected value.

### 12.1 Source Code

File:

`compare_sync.c`

The program implements four functions:

| Function | Mechanism |
|---|---|
| `run_none()` | No synchronization |
| `run_critical()` | OpenMP Critical |
| `run_atomic()` | OpenMP Atomic |
| `run_lock()` | OpenMP Lock |

### 12.2 Compilation

```bash
gcc compare_sync.c -fopenmp -o compare_sync
```

### 12.3 Execution

```bash
./compare_sync
```

### 12.4 Benchmark Configuration

| Parameter | Value |
|---|---|
| Total Increments | 10,000,000 |
| Thread Counts | 1, 2, 4, 8 |
| Synchronization Methods | 4 |
| Timing Function | `omp_get_wtime()` |
| Expected Correct Count | 10,000,000 |

## 13. Execution Steps

### 13.1 WSL Verification

Open Windows PowerShell:

```powershell
wsl --status
```

Start Ubuntu:

```powershell
wsl
```

### 13.2 Install GCC and Build Tools

Inside Ubuntu:

```bash
sudo apt update
sudo apt install build-essential -y
```

Verify GCC:

```bash
gcc --version
```

### 13.3 Create the Experiment Directory

```bash
mkdir -p ~/sync_experiment
cd ~/sync_experiment
```

### 13.4 Compile All Programs

```bash
gcc race.c -fopenmp -o race
gcc critical.c -fopenmp -o critical
gcc atomic.c -fopenmp -o atomic
gcc barrier.c -fopenmp -o barrier
gcc semaphore.c -pthread -o semaphore
gcc compare_sync.c -fopenmp -o compare_sync
```

### 13.5 Execute All Programs

```bash
OMP_NUM_THREADS=4 ./race
OMP_NUM_THREADS=4 ./critical
OMP_NUM_THREADS=4 ./atomic
OMP_NUM_THREADS=4 ./barrier
./semaphore
./compare_sync
```

## 14. Results

### 14.1 Individual Program Results

| Program | Expected Count | Observed Output | Result |
|---|---:|---:|---|
| Race Condition | 10,000,000 | 4,325,508 | Incorrect |
| Critical | 10,000,000 | 10,000,000 | Correct |
| Atomic | 10,000,000 | 10,000,000 | Correct |
| Barrier | Synchronization | All threads wait | Successful |
| Semaphore | 200,000 | 200,000 | Correct |

### 14.2 Performance Comparison Results

The following values are from the actual saved execution of `compare_sync`.

| Mechanism | Threads | Final Count | Correctness | Time (s) |
|---|---:|---:|---|---:|
| None | 1 | 10,000,000 | Correct | 0.0291 |
| Critical | 1 | 10,000,000 | Correct | 0.1693 |
| Atomic | 1 | 10,000,000 | Correct | 0.0594 |
| Lock | 1 | 10,000,000 | Correct | 0.1713 |
| None | 2 | 6,316,021 | Incorrect | 0.0312 |
| Critical | 2 | 10,000,000 | Correct | 0.3102 |
| Atomic | 2 | 10,000,000 | Correct | 0.1689 |
| Lock | 2 | 10,000,000 | Correct | 0.4681 |
| None | 4 | 2,622,866 | Incorrect | 0.0332 |
| Critical | 4 | 10,000,000 | Correct | 0.7677 |
| Atomic | 4 | 10,000,000 | Correct | 0.2413 |
| Lock | 4 | 10,000,000 | Correct | 1.0604 |
| None | 8 | 1,631,471 | Incorrect | 0.0351 |
| Critical | 8 | 10,000,000 | Correct | 0.6753 |
| Atomic | 8 | 10,000,000 | Correct | 0.2146 |
| Lock | 8 | 10,000,000 | Correct | 0.9675 |

Expected correct final count:

`10000000`

Note: Execution times and unsynchronized counter values may vary between runs and on different systems.

## 15. Performance Analysis

### 15.1 Correctness Analysis

The unsynchronized mechanism produces the correct count with one thread because there is no concurrent access.

With multiple threads, it produces incorrect results due to race conditions.

Critical, Atomic, and Lock mechanisms produce the expected count for all tested thread counts.

### 15.2 Execution Time Analysis

At 8 threads, the measured execution times were:

| Mechanism | Execution Time |
|---|---:|
| None | 0.0351 s |
| Critical | 0.6753 s |
| Atomic | 0.2146 s |
| Lock | 0.9675 s |

The unsynchronized mechanism has the lowest measured time but produces an incorrect result.

Among the correct mechanisms in this run, Atomic has the lowest execution time.

Critical and Lock introduce greater waiting and synchronization overhead.

### 15.3 Scalability Analysis

The experiment demonstrates that increasing the number of threads does not automatically improve execution time.

For this workload, all threads repeatedly update a single shared counter. This creates contention for the same memory location.

Atomic performs better than Critical and Lock in the measured multi-threaded runs, but its execution time also increases compared with the single-threaded run.

The benchmark therefore demonstrates the importance of considering contention and synchronization overhead when evaluating scalability.

### 15.4 Overall Observation

| Mechanism | Correctness | Performance Characteristics |
|---|---|---|
| None | Incorrect with concurrent updates | Low synchronization overhead |
| Critical | Correct | Waiting and serialization overhead |
| Atomic | Correct | Lower measured overhead for this workload |
| Lock | Correct | Explicit locking and waiting overhead |
| Barrier | Synchronizes execution phases | Waiting for all threads |
| Semaphore | Correct | Mutual-exclusion overhead |

## 16. Troubleshooting

| Problem | Solution |
|---|---|
| `gcc: command not found` | Install build-essential using apt |
| OpenMP compilation error | Include `-fopenmp` during compilation |
| Incorrect race condition output | This is expected when demonstrating unsynchronized access |
| Different race condition values | Race-condition output varies with thread scheduling |
| Semaphore compilation error | Include `-pthread` during compilation |
| Executable not found | Verify compilation and current directory |
| WSL filesystem read-only | Check available Windows disk space and restart WSL if needed |
| Git push rejected | Synchronize with remote changes using `git pull --rebase origin main` |

## 17. Conclusion

This experiment implemented and analyzed synchronization mechanisms used in shared-memory parallel programs.

The race condition program demonstrated how simultaneous access to shared data can result in lost updates and incorrect output.

Critical Sections, Atomic Operations, OpenMP Locks, and POSIX Semaphores ensured correct access to shared resources.

Barrier synchronization demonstrated how multiple threads can coordinate their execution phases.

The performance comparison evaluated None, Critical, Atomic, and Lock mechanisms using 1, 2, 4, and 8 threads.

The measured results showed that Atomic Operations provided the best execution time among the correct mechanisms in this benchmark run. Critical Sections and Locks introduced greater synchronization overhead due to contention.

The experiment demonstrates that synchronization is essential for correctness and that the choice of synchronization mechanism affects execution time and scalability.

## 18. Author

**Krupa Akki**

CSE (Artificial Intelligence)  
K.L.E. Technological University, Hubli

## Repository Structure

```text
PGC-Experiment-3-Synchronization-Mechanisms/
│
├── race.c
├── critical.c
├── atomic.c
├── barrier.c
├── semaphore.c
├── compare_sync.c
├── results.txt
├── README.md
│
└── screenshots/
    ├── 01_synchronization_outputs.png
    ├── 02_performance_comparison.png
    └── 03_successful_compilation.png
```

## Result Screenshots

Execution screenshots and compilation evidence are available in the `screenshots/` directory.
