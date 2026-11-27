#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <cuda_runtime.h>
#include <cmath>
#include <iomanip>

using namespace std;

#define CUDA_CHECK(call) \
do { \
    cudaError_t error = call; \
    if (error != cudaSuccess) { \
        cerr << "CUDA Error: " << cudaGetErrorString(error) \
             << " at line " << __LINE__ << endl; \
        exit(EXIT_FAILURE); \
    } \
} while (0)

__global__ void naiveConvolution(
    const unsigned char* input,
    float* output,
    int width,
    int height,
    int maskSize)
{
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;

    if (x >= width || y >= height)
        return;

    int radius = maskSize / 2;

    float sum = 0.0f;
    float weight = 1.0f / (maskSize * maskSize);

    for (int ky = -radius; ky <= radius; ky++)
    {
        for (int kx = -radius; kx <= radius; kx++)
        {
            int ix = x + kx;
            int iy = y + ky;

            if (ix >= 0 && ix < width &&
                iy >= 0 && iy < height)
            {
                sum += input[iy * width + ix];
            }
        }
    }

    output[y * width + x] = sum * weight;
}

int main()
{
    const int width = 2048;
    const int height = 2048;
    const int totalPixels = width * height;

    vector<unsigned char> input(totalPixels);

    ifstream file("images/input.raw", ios::binary);

    if (!file)
    {
        cerr << "Cannot open input image!" << endl;
        return 1;
    }

    file.read(reinterpret_cast<char*>(input.data()), totalPixels);

    if (file.gcount() != totalPixels)
    {
        cerr << "Incorrect input image size!" << endl;
        return 1;
    }

    file.close();

    unsigned char* d_input;
    float* d_output;

    CUDA_CHECK(cudaMalloc(&d_input,
        totalPixels * sizeof(unsigned char)));

    CUDA_CHECK(cudaMalloc(&d_output,
        totalPixels * sizeof(float)));

    CUDA_CHECK(cudaMemcpy(d_input, input.data(),
        totalPixels * sizeof(unsigned char),
        cudaMemcpyHostToDevice));

    dim3 block(16, 16);

    dim3 grid(
        (width + block.x - 1) / block.x,
        (height + block.y - 1) / block.y
    );

    int masks[] = {3, 5, 7};

    cout << "\nNAIVE CUDA CONVOLUTION RESULTS\n";
    cout << "---------------------------------------------\n";

    for (int mask : masks)
    {
        vector<float> output(totalPixels);

        naiveConvolution<<<grid, block>>>(
            d_input, d_output, width, height, mask);

        CUDA_CHECK(cudaGetLastError());
        CUDA_CHECK(cudaDeviceSynchronize());

        cudaEvent_t start, stop;

        CUDA_CHECK(cudaEventCreate(&start));
        CUDA_CHECK(cudaEventCreate(&stop));

        for (int i = 0; i < 5; i++)
        {
            naiveConvolution<<<grid, block>>>(
                d_input, d_output, width, height, mask);
        }

        CUDA_CHECK(cudaDeviceSynchronize());

        CUDA_CHECK(cudaEventRecord(start));

        const int iterations = 20;

        for (int i = 0; i < iterations; i++)
        {
            naiveConvolution<<<grid, block>>>(
                d_input, d_output, width, height, mask);
        }

        CUDA_CHECK(cudaEventRecord(stop));
        CUDA_CHECK(cudaEventSynchronize(stop));

        float elapsed = 0.0f;

        CUDA_CHECK(cudaEventElapsedTime(&elapsed, start, stop));

        CUDA_CHECK(cudaMemcpy(output.data(), d_output,
            totalPixels * sizeof(float),
            cudaMemcpyDeviceToHost));

        float centerPixel = output[(height / 2) * width + width / 2];

        cout << fixed << setprecision(4);

        cout << "Mask: " << mask << "x" << mask
             << " | Average GPU Time: "
             << elapsed / iterations << " ms"
             << " | Center Pixel: " << centerPixel
             << endl;

        CUDA_CHECK(cudaEventDestroy(start));
        CUDA_CHECK(cudaEventDestroy(stop));

        string filename = "output/naive_" +
                          to_string(mask) + "x" +
                          to_string(mask) + ".raw";

        ofstream outFile(filename, ios::binary);

        outFile.write(
            reinterpret_cast<const char*>(output.data()),
            totalPixels * sizeof(float));

        outFile.close();
    }

    CUDA_CHECK(cudaFree(d_input));
    CUDA_CHECK(cudaFree(d_output));

    cout << "\nNaive CUDA convolution completed!" << endl;

    return 0;
}
