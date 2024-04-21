#include <cstdint>
#include <vector>
#include <fstream>
#include <iostream>
#include <string>
#include <math.h>
#include <chrono>
#include <cstdio>
#include "json.hpp"

using namespace std;
using json = nlohmann::json;

const int progressBarWidth = 70;

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

void createVideoFromFrames(int framerate, const string& outputFilename) {
  cout << "\nEncoding video..." << endl;
  string ffmpegCmd = "ffmpeg -y -loglevel info -framerate " + to_string(framerate) + " -i frames/frame%d.ppm -c:v libx264 -pix_fmt yuv420p " + outputFilename + " 2>&1";
  
  FILE* pipe = _popen(ffmpegCmd.c_str(), "r");
  if (!pipe) {
      cerr << "Error: Could not open pipe for FFmpeg." << endl;
      return;
  }

  char buffer[128];
  while (!feof(pipe)) {
      if (fgets(buffer, 128, pipe) != nullptr) {
          string line(buffer);
          if (line.find("frame=") != string::npos || line.find("fps=") != string::npos) {
              cout << line; // Display only progress-related lines
          }
      }
  }

  _pclose(pipe);

  cout << endl << outputFilename << " encoded successfully." << endl;
}

void displayProgress(int current, int total, TimePoint startTime) {
    int barWidth = 50;
    float progress = (float)current / total;

    TimePoint currentTime = Clock::now();
    auto elapsedTime = duration_cast<seconds>(currentTime - startTime).count();
    auto estimatedTotalTime = static_cast<int>(elapsedTime / progress);
    auto remainingTime = estimatedTotalTime - elapsedTime;

    cout << "Rendering video... [";
    int pos = barWidth * progress;
    for (int i = 0; i < barWidth; ++i) {
        if (i < pos) cout << "=";
        else if (i == pos) cout << ">";
        else cout << " ";
    }
    cout << "] " << int(progress * 100.0) << " % - Elapsed: " << elapsedTime << "s, Remaining: " << remainingTime << "s \r";
    cout.flush();
}

int main() {
  // Reading the configuration from the JSON file
  ifstream configFile("config.json");
  if (!configFile.is_open()) {
      cerr << "Error opening config file" << endl;
      return 1;
  }

  json config;
  configFile >> config;

  int width = config["frame_width"];
  int height = config["frame_height"];
  int videoLength = config["videoLength"]; // Video length in seconds
  int framerate = config["framerate"];
  double amplitude = double(config["amplitude"]) / 100.0; // Convert percentage to a fraction
  double frequency = config["frequency"]; // Number of peaks per frame
  int numFrames = videoLength * framerate; // Calculating number of frames

  // Extracting RGB color values
  Pixel aboveSineWave = {
    config["colors"]["aboveSineWave"][0],
    config["colors"]["aboveSineWave"][1],
    config["colors"]["aboveSineWave"][2]
  };

  Pixel borderLine = {
    config["colors"]["borderLine"][0],
    config["colors"]["borderLine"][1],
    config["colors"]["borderLine"][2]
  };

  Pixel belowSineWave = {
    config["colors"]["belowSineWave"][0],
    config["colors"]["belowSineWave"][1],
    config["colors"]["belowSineWave"][2]
  };
  
  const double sineFrequency = frequency * 2 * 3.14159265 / width; // Adjust frequency based on frame width

  vector<vector<Pixel>> frame(height, vector<Pixel>(width));

  TimePoint startTime = Clock::now();

  for (int i = 0; i < numFrames; ++i) {
      double phaseShift = i * 0.1; // Phase shift changes in each frame

      for (int y = 0; y < height; ++y) {
          for (int x = 0; x < width; ++x) {
              double sineValue = sin(sineFrequency * x + phaseShift) * amplitude * (height / 2) + (height / 2);
              Pixel& pixel = frame[y][x];

              if (abs(y - sineValue) < 10) { // Pixel is on the sine wave
                pixel = borderLine;
              } else if (y > sineValue) { // Pixel is below the sine wave
                pixel = belowSineWave;
              } else { // Pixel is above the sine wave
                pixel = aboveSineWave;
              }
          }
      }

      writeFrame(frame, "frames/frame" + to_string(i) + ".ppm");
      displayProgress(i + 1, numFrames, startTime);
  }

  cout << "\n" << numFrames << " frames rendered successfully." << endl;
  
  createVideoFromFrames(framerate, "output.mp4");

  cout << endl;
  system("pause");

  return 0;
}