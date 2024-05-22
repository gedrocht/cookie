#include <iostream>
#include <iomanip>
#include <bitset>
#include <string>
#include <cstring>
#include <cstdlib>
#include <chrono>
#include <vector>
#include <thread>
#include <cmath>
#include <numeric>
#include <fftw3.h>

#ifdef _WIN32
#define _WINSOCKAPI_
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <audioclient.h>
#include <mmdeviceapi.h>
#include <endpointvolume.h>
#include <functiondiscoverykeys_devpkey.h>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "ole32.lib")
#endif

using namespace std;

#define FRAME_DELAY 30
#define BUFFER_SIZE 48000

bool initializeAudioCapture(IAudioClient** audioClient, IAudioCaptureClient** captureClient, IMMDevice* device, bool loopback) {
    HRESULT hr;

    // Activate audio client
    hr = device->Activate(__uuidof(IAudioClient), CLSCTX_ALL, nullptr, (void**)audioClient);
    if (FAILED(hr)) {
        cerr << "Failed to activate audio client." << endl;
        return false;
    }

    // Get audio format
    WAVEFORMATEX* waveFormat;
    hr = (*audioClient)->GetMixFormat(&waveFormat);
    if (FAILED(hr)) {
        cerr << "Failed to get audio format." << endl;
        (*audioClient)->Release();
        return false;
    }

    // Initialize audio client
    hr = (*audioClient)->Initialize(AUDCLNT_SHAREMODE_SHARED, loopback ? AUDCLNT_STREAMFLAGS_LOOPBACK : 0, 10000000, 0, waveFormat, nullptr);
    if (FAILED(hr)) {
        cerr << "Failed to initialize audio client." << endl;
        CoTaskMemFree(waveFormat);
        (*audioClient)->Release();
        return false;
    }

    // Get audio capture client
    hr = (*audioClient)->GetService(__uuidof(IAudioCaptureClient), (void**)captureClient);
    if (FAILED(hr)) {
        cerr << "Failed to get audio capture client." << endl;
        CoTaskMemFree(waveFormat);
        (*audioClient)->Release();
        return false;
    }

    // Start audio client
    hr = (*audioClient)->Start();
    if (FAILED(hr)) {
        cerr << "Failed to start audio client." << endl;
        (*captureClient)->Release();
        CoTaskMemFree(waveFormat);
        (*audioClient)->Release();
        return false;
    }

    CoTaskMemFree(waveFormat);
    return true;
}

void listAudioDevices(IMMDeviceEnumerator* deviceEnumerator, vector<IMMDevice*>& devices, EDataFlow dataFlow) {
    IMMDeviceCollection* deviceCollection = nullptr;
    HRESULT hr = deviceEnumerator->EnumAudioEndpoints(dataFlow, DEVICE_STATE_ACTIVE, &deviceCollection);
    if (FAILED(hr)) {
        cerr << "Failed to enumerate audio endpoints." << endl;
        return;
    }

    UINT deviceCount;
    hr = deviceCollection->GetCount(&deviceCount);
    if (FAILED(hr)) {
        cerr << "Failed to get device count." << endl;
        deviceCollection->Release();
        return;
    }

    for (UINT i = 0; i < deviceCount; ++i) {
        IMMDevice* device = nullptr;
        hr = deviceCollection->Item(i, &device);
        if (SUCCEEDED(hr)) {
            LPWSTR deviceId = nullptr;
            hr = device->GetId(&deviceId);
            if (SUCCEEDED(hr)) {
                IPropertyStore* propertyStore = nullptr;
                hr = device->OpenPropertyStore(STGM_READ, &propertyStore);
                if (SUCCEEDED(hr)) {
                    PROPVARIANT friendlyName;
                    PropVariantInit(&friendlyName);
                    hr = propertyStore->GetValue(PKEY_Device_FriendlyName, &friendlyName);
                    if (SUCCEEDED(hr)) {
                        wcout << L"[" << i << L"] " << friendlyName.pwszVal << endl;
                        PropVariantClear(&friendlyName);
                    }
                    propertyStore->Release();
                }
                CoTaskMemFree(deviceId);
            }
            devices.push_back(device);
        }
    }
    deviceCollection->Release();
}

double calculateVolume(const BYTE* data, size_t numFrames, int numChannels, int bytesPerSample) {
    double rms = 0.0;
    size_t count = numFrames * numChannels;

    // Ensure that the data buffer is not empty to avoid division by zero
    if (data == nullptr || count == 0) {
        cerr << "Empty or null data buffer." << endl;
        return -1.0;  // Return -1 to indicate an error
    }

    for (size_t i = 0; i < count; ++i) {
        float sample = 0.0f;
        memcpy(&sample, data + i * bytesPerSample, bytesPerSample);
        rms += sample * sample;
    }

    rms = sqrt(rms / count);
    return rms;
}

// Function to calculate dominant frequency using FFT and map it to a logarithmic scale
int calculateLogarithmicFrequency(const BYTE* data, UINT32 numFrames, WAVEFORMATEX* waveFormat) {
    int N = numFrames;
    double* in = (double*)fftw_malloc(sizeof(double) * N);
    fftw_complex* out = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * N);
    fftw_plan plan = fftw_plan_dft_r2c_1d(N, in, out, FFTW_ESTIMATE);

    // Fill the input array with audio data
    for (UINT32 i = 0; i < numFrames; ++i) {
        if (waveFormat->wBitsPerSample == 16) {
            in[i] = ((short*)data)[i];
        }
        else if (waveFormat->wBitsPerSample == 32) {
            in[i] = ((float*)data)[i];
        }
    }

    fftw_execute(plan); // Perform FFT

    // Find the peak frequency bin
    double maxMagnitude = 0.0;
    int peakIndex = 0;
    for (int i = 0; i < N / 2; ++i) {
        double magnitude = sqrt(out[i][0] * out[i][0] + out[i][1] * out[i][1]);
        if (magnitude > maxMagnitude) {
            maxMagnitude = magnitude;
            peakIndex = i;
        }
    }

    // Convert bin index to frequency
    double frequency = (double)peakIndex * waveFormat->nSamplesPerSec / N;

    fftw_destroy_plan(plan);
    fftw_free(in);
    fftw_free(out);

    // Map the frequency to a logarithmic scale between 0 and 255
    const double minFreq = 20.0;
    const double maxFreq = 10000.0;
    double logMinFreq = log10(minFreq);
    double logMaxFreq = log10(maxFreq);
    double logFrequency = log10(frequency);

    int logFrequencyValue = (int)((logFrequency - logMinFreq) / (logMaxFreq - logMinFreq) * 255);
    logFrequencyValue = max(0, min(255, logFrequencyValue)); // Clamp to [0, 255]

    return logFrequencyValue;
}

bool sendUint32(SOCKET sock, uint32_t value) {
    int sendRes = send(sock, reinterpret_cast<const char*>(&value), sizeof(value), 0);
    if (sendRes == SOCKET_ERROR) {
        std::cerr << "Send failed: " << WSAGetLastError() << std::endl;
        return false;
    }
    return true;
}

int main() {
    // Initialize COM library
    HRESULT hr = CoInitialize(nullptr);
    if (FAILED(hr)) {
        // Handle the COM initialization error
        fprintf(stderr, "CoInitialize failed with error: 0x%lx\n", hr);
        // Cleanup Winsock if COM initialization fails
        WSACleanup();
        exit(EXIT_FAILURE); // or return from the function if it is not the main function
    }

    // Initialize Winsock for network communication
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        // Handle the error, for example, by printing an error message and exiting the program
        fprintf(stderr, "WSAStartup failed with error: %d\n", result);
        exit(EXIT_FAILURE); // or return from the function if it is not the main function
    }

    // Create a TCP socket
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        cerr << "Can't create socket, Err #" << WSAGetLastError() << endl;
        CoUninitialize();
        return 1;
    }

    // Configure server address
    string ipAddress = "127.0.0.1"; // Localhost
    int port = 1989; // Port number
    sockaddr_in hint = {};
    hint.sin_family = AF_INET;
    hint.sin_port = htons(port);
    inet_pton(AF_INET, ipAddress.c_str(), &hint.sin_addr);

    // Connect to the server
    if (connect(sock, (sockaddr*)&hint, sizeof(hint)) == SOCKET_ERROR) {
        cerr << "Can't connect, Err #" << WSAGetLastError() << endl;
        closesocket(sock);
        CoUninitialize();
        return 1;
    }

    // Create device enumerator
    IMMDeviceEnumerator* deviceEnumerator = nullptr;
    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_INPROC_SERVER, __uuidof(IMMDeviceEnumerator), (void**)&deviceEnumerator);
    if (FAILED(hr)) {
        cerr << "Failed to create device enumerator." << endl;
        closesocket(sock);
        CoUninitialize();
        return 1;
    }

    // Ask the user to select input or output devices
    int deviceType;
    cout << "Select device type:\n1. Output\n2. Input\nChoice: ";
    cin >> deviceType;
    EDataFlow dataFlow = (deviceType == 1) ? eRender : eCapture;
    bool loopback = (deviceType == 1);

    // List available devices based on user selection
    vector<IMMDevice*> devices;
    listAudioDevices(deviceEnumerator, devices, dataFlow);
    if (devices.empty()) {
        cerr << "No devices found." << endl;
        deviceEnumerator->Release();
        closesocket(sock);
        CoUninitialize();
        return 1;
    }

    // Select the desired device
    int selectedDeviceIndex;
    cout << "Select device index: ";
    cin >> selectedDeviceIndex;
    if (selectedDeviceIndex < 0 || selectedDeviceIndex >= static_cast<int>(devices.size())) {
        cerr << "Invalid device index." << endl;
        deviceEnumerator->Release();
        closesocket(sock);
        CoUninitialize();
        return 1;
    }
    IMMDevice* selectedDevice = devices[selectedDeviceIndex];

    // Initialize audio capture
    IAudioClient* audioClient = nullptr;
    IAudioCaptureClient* captureClient = nullptr;
    if (!initializeAudioCapture(&audioClient, &captureClient, selectedDevice, loopback)) {
        cerr << "Audio capture initialization failed." << endl;
        deviceEnumerator->Release();
        closesocket(sock);
        CoUninitialize();
        return 1;
    }

    UINT32 packetLength = 0;
    DWORD flags;

    vector<double> volumeValues;
    vector<double> frequencyValues;
    auto lastSendTime = chrono::steady_clock::now();

    // Main loop to capture audio and send volume data
    while (true) {
        // Get the next packet size
        hr = captureClient->GetNextPacketSize(&packetLength);
        if (FAILED(hr)) {
            cerr << "Failed to get next packet size." << endl;
            break;
        }

        while (packetLength != 0) {
            BYTE* data;
            UINT32 numFrames;
            hr = captureClient->GetBuffer(&data, &numFrames, &flags, nullptr, nullptr);
            if (FAILED(hr)) {
                cerr << "Failed to get buffer." << endl;
                break;
            }

            // Calculate volume
            double volume = calculateVolume(data, numFrames, 2, 4); // Using float (4 bytes) samples
            volumeValues.push_back(volume);

            WAVEFORMATEX* waveFormat;
            audioClient->GetMixFormat(&waveFormat);
            double frequency = calculateLogarithmicFrequency(data, numFrames, waveFormat);
            frequencyValues.push_back(frequency);

            hr = captureClient->ReleaseBuffer(numFrames);
            if (FAILED(hr)) {
                cerr << "Failed to release buffer." << endl;
                break;
            }

            hr = captureClient->GetNextPacketSize(&packetLength);
            if (FAILED(hr)) {
                cerr << "Failed to get next packet size." << endl;
                break;
            }
        }

        auto now = chrono::steady_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(now - lastSendTime).count();
        if (duration >= FRAME_DELAY) {
            if (!volumeValues.empty()) {
                float averageVolume = static_cast<float>(accumulate(volumeValues.begin(), volumeValues.end(), 0.0) / volumeValues.size());
                averageVolume /= 0.00025f;
                if (averageVolume > 255) {
                    averageVolume = 255;
                }
                float averageFrequency = static_cast<float>(accumulate(frequencyValues.begin(), frequencyValues.end(), 0.0) / frequencyValues.size());

                UINT32 ui_volume = static_cast<UINT32>(averageVolume);
                //cout << bitset<32>(ui_volume).to_string() << endl;
                UINT32 ui_frequency = static_cast<UINT32>(averageFrequency);
                ui_frequency <<= 8;
                //cout << bitset<32>(ui_frequency).to_string() << endl;
                if (!sendUint32(sock, ui_volume | ui_frequency)) {
                    break;
                }

                volumeValues.clear();
                frequencyValues.clear();
            }
            lastSendTime = now;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(FRAME_DELAY));
    }

    // Clean up resources
    audioClient->Stop();
    captureClient->Release();
    audioClient->Release();
    deviceEnumerator->Release();
    closesocket(sock);
    WSACleanup();
    CoUninitialize();
    return 0;
}
