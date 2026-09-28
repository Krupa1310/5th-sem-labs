# matrix-multiplication-lab
# Matrix Multiplication using Sequential, OpenMP and MPI

## About the Project

This project implements matrix multiplication using different computing approaches and compares their execution performance.

The implementations covered in this project are:

* Sequential Programming
* OpenMP Parallel Programming
* MPI (Message Passing Interface)

## Matrix Details

* Matrix size: 4000 × 4000
* Matrix A elements: 1.0
* Matrix B elements: 1.0
* Expected verification result: `C[0][0] = 4000.00`

## Implementations

### 1. Sequential

The sequential implementation performs matrix multiplication using a single process without parallelization.

### 2. OpenMP

The OpenMP implementation uses multiple CPU threads to perform matrix multiplication in parallel.

### 3. MPI

The MPI implementation distributes the matrix multiplication across multiple processes running on different machines/nodes.

## Project Structure

```text
matrix-multiplication-lab/
│
├── README.md
│
├── sequential/
│   ├── matrix_sequential.c
│   └── matrix_sequential
│
├── openmp/
│   ├── matrix_openmp.c
│   └── matrix_openmp
│
└── mpi/
    └── (MPI implementation)
```

## Results

| Implementation | Matrix Size |     Execution Time |
| -------------- | ----------: | -----------------: |
| Sequential     | 4000 × 4000 | 553.956974 seconds |
| OpenMP         | 4000 × 4000 | 634.083018 seconds |
| MPI            | 4000 × 4000 |     To be measured |

### Verification

The completed Sequential and OpenMP implementations produced:

```text
C[0][0] = 4000.00
```

## Objective

The objective of this experiment is to implement matrix multiplication using sequential and parallel computing techniques and study their execution performance.

## Technologies Used

* C
* OpenMP
* MPI
* GCC
* Ubuntu/Linux
* Git and GitHub

## Status

* [ ] Sequential implementation
* [ ] OpenMP implementation
* [ ] MPI implementation

