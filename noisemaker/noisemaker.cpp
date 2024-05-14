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

#define FRAME_DELAY 15
#define BUFFER_SIZE 48000

bool initializeAudioCapture(IAudioClient** audioClient, IAudioCaptureClient** captureClient, IMMDevice* device) {
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

    // Initialize audio client in loopback mode
    hr = (*audioClient)->Initialize(AUDCLNT_SHAREMODE_SHARED, AUDCLNT_STREAMFLAGS_LOOPBACK, 10000000, 0, waveFormat, nullptr);
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

void listAudioDevices(IMMDeviceEnumerator* deviceEnumerator, vector<IMMDevice*>& devices) {
    IMMDeviceCollection* deviceCollection = nullptr;
    HRESULT hr = deviceEnumerator->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, &deviceCollection);
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

void sendUint32(SOCKET sock, uint32_t value) {
    int sendRes = send(sock, reinterpret_cast<const char*>(&value), sizeof(value), 0);
    if (sendRes == SOCKET_ERROR) {
        std::cerr << "Send failed: " << WSAGetLastError() << std::endl;
    }
}

int main() {
    // Initialize COM library
    CoInitialize(nullptr);

    // Initialize Winsock for network communication
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

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
    sockaddr_in hint;
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
    HRESULT hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_INPROC_SERVER, __uuidof(IMMDeviceEnumerator), (void**)&deviceEnumerator);
    if (FAILED(hr)) {
        cerr << "Failed to create device enumerator." << endl;
        closesocket(sock);
        CoUninitialize();
        return 1;
    }

    // List available playback devices
    vector<IMMDevice*> devices;
    listAudioDevices(deviceEnumerator, devices);
    if (devices.empty()) {
        cerr << "No playback devices found." << endl;
        deviceEnumerator->Release();
        closesocket(sock);
        CoUninitialize();
        return 1;
    }

    // Select the desired playback device
    int selectedDeviceIndex;
    cout << "Select playback device index: ";
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
    if (!initializeAudioCapture(&audioClient, &captureClient, selectedDevice)) {
        cerr << "Audio capture initialization failed." << endl;
        deviceEnumerator->Release();
        closesocket(sock);
        CoUninitialize();
        return 1;
    }

    // Buffer for audio data
    BYTE buffer[BUFFER_SIZE];
    UINT32 packetLength = 0;
    DWORD flags;

    vector<double> volumeValues;
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
            if (volume >= 0) {
                volumeValues.push_back(volume);
            }

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
                averageVolume /= 0.00006f;
                if (averageVolume > 255) {
                    averageVolume = 255;
                }

                UINT32 ui_volume = static_cast<UINT32>(averageVolume);
                cout << bitset<32>(ui_volume).to_string() << endl;
                sendUint32(sock, ui_volume);
                
                volumeValues.clear();
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
