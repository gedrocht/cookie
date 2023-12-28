#include <cstdint>
#include <vector>
#include <fstream>
#include <iostream>
#include <string>
#include <math.h>
#include <chrono>
using namespace std;

const int height = 1080;
const int width = 1920;
const int numFrames = 600;
const int progressBarWidth = 70;
const double frequency = 2 * 3.14159265 / width;

struct Pixel {
    uint8_t r, g, b;
};

using Clock = chrono::steady_clock;
using TimePoint = chrono::time_point<Clock>;
using chrono::duration_cast;
using chrono::seconds;

void writeFrame(const vector<vector<Pixel>>& frame, const string& filename) {
    ofstream file(filename, ios::binary);
    if (!file) {
        cerr << "Error opening file: " << filename << endl;
        return;
    }

    // Simple PPM format (P6)
    file << "P6\n" << frame[0].size() << " " << frame.size() << "\n255\n";

    for (const auto& row : frame) {
        for (const auto& pixel : row) {
            file.write(reinterpret_cast<const char*>(&pixel), sizeof(Pixel));
        }
    }
}

void createVideoFromFrames(int numFrames, const string& outputFilename) {
    cout << "Creating video, please wait..." << endl;
    string ffmpegCmd = "ffmpeg -y -framerate 60 -i frames/frame%d.ppm -c:v libx264 -pix_fmt yuv420p " + outputFilename;
    system(ffmpegCmd.c_str());
}

void displayProgress(int current, int total, TimePoint startTime) {
    int barWidth = 70;
    float progress = (float)current / total;

    TimePoint currentTime = Clock::now();
    auto elapsedTime = duration_cast<seconds>(currentTime - startTime).count();
    auto estimatedTotalTime = static_cast<int>(elapsedTime / progress);
    auto remainingTime = estimatedTotalTime - elapsedTime;

    cout << "[";
    int pos = barWidth * progress;
    for (int i = 0; i < barWidth; ++i) {
        if (i < pos) cout << "=";
        else if (i == pos) cout << ">";
        else cout << " ";
    }
    cout << "] " << int(progress * 100.0) << " % - Elapsed: " << elapsedTime << "s, Remaining: " << remainingTime << "s\r";
    cout.flush();
}

int main() {
  vector<vector<Pixel>> frame(height, vector<Pixel>(width));

  TimePoint startTime = Clock::now();

  for (int i = 0; i < numFrames; ++i) {
      double phaseShift = i * 0.1; // Phase shift changes in each frame

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                double sineValue = std::sin(frequency * x + phaseShift) * (height / 4) + (height / 2);
                Pixel& pixel = frame[y][x];

                if (std::abs(y - sineValue) < 10) { // Pixel is on the sine wave
                    pixel.r = 255; pixel.g = 0; pixel.b = 0;
                } else if (y > sineValue) { // Pixel is below the sine wave
                    pixel.r = 0; pixel.g = 255; pixel.b = 0;
                } else { // Pixel is above the sine wave
                    pixel.r = 0; pixel.g = 0; pixel.b = 255;
                }
            }
        }

      writeFrame(frame, "frames/frame" + std::to_string(i) + ".ppm");
      displayProgress(i + 1, numFrames, startTime);
  }
  
  createVideoFromFrames(numFrames, "output.mp4");

  return 0;
}