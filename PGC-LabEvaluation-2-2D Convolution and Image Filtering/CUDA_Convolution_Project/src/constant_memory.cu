
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cuda_runtime.h>

using namespace std;

#define CHECK(call) \
{ \
    cudaError_t error = call; \
    if (error != cudaSuccess) \
    { \
        cerr << "CUDA Error: " << cudaGetErrorString(error) << endl; \
        exit(1); \
    } \
}

__constant__ float d_mask[49];

__global__ void convolutionConstant(
    const unsigned char* input,
    float* output,
    int width,
    int height,
    int maskSize)
{
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;

    if (x < width && y < height)
    {
        int radius = maskSize / 2;
        float sum = 0.0f;

        for (int ky = -radius; ky <= radius; ky++)
        {
            for (int kx = -radius; kx <= radius; kx++)
            {
                int ix = x + kx;
                int iy = y + ky;

                if (ix >= 0 && ix < width &&
                    iy >= 0 && iy < height)
                {
                    int maskIndex =
                        (ky + radius) * maskSize + (kx + radius);

                    sum += input[iy * width + ix] *
                           d_mask[maskIndex];
                }
            }
        }

        output[y * width + x] = sum;
    }
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
        cout << "Error opening input image!" << endl;
        return 1;
    }

    file.read(reinterpret_cast<char*>(input.data()), totalPixels);
    file.close();

    unsigned char* d_input;
    float* d_output;

    CHECK(cudaMalloc(&d_input, totalPixels * sizeof(unsigned char)));
    CHECK(cudaMalloc(&d_output, totalPixels * sizeof(float)));

    CHECK(cudaMemcpy(
        d_input, input.data(),
        totalPixels * sizeof(unsigned char),
        cudaMemcpyHostToDevice));

    dim3 block(16, 16);

    dim3 grid(
        (width + block.x - 1) / block.x,
        (height + block.y - 1) / block.y
    );

    int masks[] = {3, 5, 7};

    cout << "\nCONSTANT MEMORY CUDA RESULTS\n";
    cout << "---------------------------------------------\n";

    for (int maskSize : masks)
    {
        float weight = 1.0f / (maskSize * maskSize);

        vector<float> mask(maskSize * maskSize, weight);

        CHECK(cudaMemcpyToSymbol(
            d_mask,
            mask.data(),
            mask.size() * sizeof(float)
        ));

        for (int i = 0; i < 5; i++)
        {
            convolutionConstant<<<grid, block>>>(
                d_input, d_output, width, height, maskSize);
        }

        CHECK(cudaDeviceSynchronize());

        cudaEvent_t start, stop;

        CHECK(cudaEventCreate(&start));
        CHECK(cudaEventCreate(&stop));

        CHECK(cudaEventRecord(start));

        for (int i = 0; i < 20; i++)
        {
            convolutionConstant<<<grid, block>>>(
                d_input, d_output, width, height, maskSize);
        }

        CHECK(cudaEventRecord(stop));
        CHECK(cudaEventSynchronize(stop));

        float totalTime = 0.0f;

        CHECK(cudaEventElapsedTime(&totalTime, start, stop));

        float averageTime = totalTime / 20.0f;

        vector<float> output(totalPixels);

        CHECK(cudaMemcpy(
            output.data(),
            d_output,
            totalPixels * sizeof(float),
            cudaMemcpyDeviceToHost));

        string filename = "output/constant_" +
                          to_string(maskSize) + "x" +
                          to_string(maskSize) + ".raw";

        ofstream outputFile(filename, ios::binary);

        outputFile.write(
            reinterpret_cast<const char*>(output.data()),
            output.size() * sizeof(float));

        outputFile.close();

        cout << "Mask: " << maskSize << "x" << maskSize
             << " | Average GPU Time: " << averageTime << " ms"
             << " | Center Pixel: "
             << output[(height / 2) * width + width / 2]
             << endl;

        cudaEventDestroy(start);
        cudaEventDestroy(stop);
    }

    cudaFree(d_input);
    cudaFree(d_output);

    cout << "\nConstant Memory convolution completed!" << endl;

    return 0;
}
