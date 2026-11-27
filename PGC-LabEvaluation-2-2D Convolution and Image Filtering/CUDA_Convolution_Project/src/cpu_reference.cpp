#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <cmath>
#include <string>

using namespace std;

void convolutionCPU(
    const vector<unsigned char>& input,
    vector<float>& output,
    int width,
    int height,
    int maskSize)
{
    int radius = maskSize / 2;
    float weight = 1.0f / (maskSize * maskSize);

    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
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
                        sum += input[iy * width + ix];
                    }
                }
            }

            output[y * width + x] = sum * weight;
        }
    }
}

int main()
{
    const int width = 2048;
    const int height = 2048;

    vector<unsigned char> input(width * height);

    ifstream file("images/input.raw", ios::binary);

    if (!file)
    {
        cout << "Error opening input image!" << endl;
        return 1;
    }

    file.read(reinterpret_cast<char*>(input.data()), input.size());
    file.close();

    int masks[] = {3, 5, 7};

    cout << "\nCPU CONVOLUTION RESULTS\n";
    cout << "-------------------------------\n";

    for (int mask : masks)
    {
        vector<float> output(width * height);

        auto start = chrono::high_resolution_clock::now();

        convolutionCPU(input, output, width, height, mask);

        auto end = chrono::high_resolution_clock::now();

        double time = chrono::duration<double, milli>(
            end - start).count();

        string filename = "output/cpu_" +
                          to_string(mask) + "x" +
                          to_string(mask) + ".raw";

        ofstream outputFile(filename, ios::binary);

        if (!outputFile)
        {
            cout << "Error saving " << filename << endl;
            return 1;
        }

        outputFile.write(
            reinterpret_cast<const char*>(output.data()),
            output.size() * sizeof(float));

        outputFile.close();

        cout << "Mask: " << mask << "x" << mask
             << " | Time: " << time << " ms"
             << " | Center pixel: "
             << output[(height / 2) * width + width / 2]
             << " | Saved: " << filename
             << endl;
    }

    cout << "\nCPU convolution completed!" << endl;

    return 0;
}
