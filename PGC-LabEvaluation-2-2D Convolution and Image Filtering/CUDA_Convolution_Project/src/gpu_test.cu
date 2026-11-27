#include <stdio.h>
#include <cuda_runtime.h>

__global__ void testKernel(int *data)
{
    int i = threadIdx.x;
    data[i] = i * i;
}

int main()
{
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, 0);

    printf("GPU Name: %s\n", prop.name);

    int *d_data;
    int h_data[5];

    cudaMalloc(&d_data, 5 * sizeof(int));

    testKernel<<<1, 5>>>(d_data);

    cudaDeviceSynchronize();

    cudaMemcpy(h_data, d_data, 5 * sizeof(int),
               cudaMemcpyDeviceToHost);

    printf("\nCUDA Kernel Results:\n");

    for (int i = 0; i < 5; i++)
    {
        printf("%d ", h_data[i]);
    }

    printf("\n");

    cudaFree(d_data);

    return 0;
}
