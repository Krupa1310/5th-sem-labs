
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

#define TILE_SIZE 16
#define MAX_RADIUS 3
#define SHARED_SIZE (TILE_SIZE + 2 * MAX_RADIUS)

__global__ void convolutionShared(
    const unsigned char* input,
    float* output,
    int width,
    int height,
    int maskSize)
{
    __shared__ unsigned char tile[SHARED_SIZE][SHARED_SIZE];

    int radius = maskSize / 2;

    int tx = threadIdx.x;
    int ty = threadIdx.y;

    int x = blockIdx.x * TILE_SIZE + tx;
    int y = blockIdx.y * TILE_SIZE + ty;

    int sharedX = tx + MAX_RADIUS;
    int sharedY = ty + MAX_RADIUS;

    tile[sharedY][sharedX] =
        (x < width && y < height)
        ? input[y * width + x]
        : 0;

    if (tx < MAX_RADIUS)
    {
        int leftX = x - MAX_RADIUS;
        int rightX = x + TILE_SIZE;

        tile[sharedY][tx] =
            (leftX >= 0 && y < height)
            ? input[y * width + leftX]
            : 0;

        tile[sharedY][sharedX + TILE_SIZE] =
            (rightX < width && y < height)
            ? input[y * width + rightX]
            : 0;
    }

    if (ty < MAX_RADIUS)
    {
        int topY = y - MAX_RADIUS;
        int bottomY = y + TILE_SIZE;

        tile[ty][sharedX] =
            (topY >= 0 && x < width)
            ? input[topY * width + x]
            : 0;

        tile[sharedY + TILE_SIZE][sharedX] =
            (bottomY < height && x < width)
            ? input[bottomY * width + x]
            : 0;
    }

    if (tx < MAX_RADIUS && ty < MAX_RADIUS)
    {
        int leftX = x - MAX_RADIUS;
        int rightX = x + TILE_SIZE;
        int topY = y - MAX_RADIUS;
        int bottomY = y + TILE_SIZE;

        tile[ty][tx] =
            (leftX >= 0 && topY >= 0)
            ? input[topY * width + leftX]
            : 0;

        tile[ty][sharedX + TILE_SIZE] =
            (rightX < width && topY >= 0)
            ? input[topY * width + rightX]
            : 0;

        tile[sharedY + TILE_SIZE][tx] =
            (leftX >= 0 && bottomY < height)
            ? input[bottomY * width + leftX]
            : 0;

        tile[sharedY + TILE_SIZE][sharedX + TILE_SIZE] =
            (rightX < width && bottomY < height)
            ? input[bottomY * width + rightX]
            : 0;
    }

    __syncthreads();

    if (x < width && y < height)
    {
        float sum = 0.0f;

        for (int ky = -radius; ky <= radius; ky++)
        {
            for (int kx = -radius; kx <= radius; kx++)
            {
                int sx = sharedX + kx;
                int sy = sharedY + ky;

                sum += tile[sy][sx];
            }
        }

        output[y * width + x] =
            sum / (maskSize * maskSize);
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
        d_input,
        input.data(),
        totalPixels * sizeof(unsigned char),
        cudaMemcpyHostToDevice));

    dim3 block(TILE_SIZE, TILE_SIZE);

    dim3 grid(
        (width + TILE_SIZE - 1) / TILE_SIZE,
        (height + TILE_SIZE - 1) / TILE_SIZE
    );

    int masks[] = {3, 5, 7};

    cout << "\nSHARED MEMORY CUDA RESULTS\n";
    cout << "---------------------------------------------\n";

    for (int maskSize : masks)
    {
        for (int i = 0; i < 5; i++)
        {
            convolutionShared<<<grid, block>>>(
                d_input,
                d_output,
                width,
                height,
                maskSize);
        }

        CHECK(cudaDeviceSynchronize());

        cudaEvent_t start, stop;

        CHECK(cudaEventCreate(&start));
        CHECK(cudaEventCreate(&stop));

        CHECK(cudaEventRecord(start));

        for (int i = 0; i < 20; i++)
        {
            convolutionShared<<<grid, block>>>(
                d_input,
                d_output,
                width,
                height,
                maskSize);
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

        string filename = "output/shared_" +
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

    cout << "\nShared Memory convolution completed!" << endl;

    return 0;
}
