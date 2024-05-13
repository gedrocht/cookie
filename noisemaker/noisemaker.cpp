#include <iostream>    // Standard I/O operations
#include <iomanip>     // Input/output manipulations
#include <string>      // String operations
#include <cstring>     // String manipulation functions
#include <cstdlib>     // General-purpose functions including memory management, program control, etc.
#include <chrono>      // Handling time, useful for timing operations
#include <thread>      // For managing threading
#include <cmath>       // For mathematical operations such as std::abs and std::sqrt

// Windows specific headers for audio and network
#ifdef _WIN32
#define _WINSOCKAPI_   // Prevent inclusion of winsock.h in windows.h
#include <winsock2.h>  // Winsock2 for network communications
#include <ws2tcpip.h>  // Definitions for network protocols
#include <windows.h>   // Windows API is required for many Windows functions
#include <Audioclient.h> // WASAPI audio client interfaces
#include <Mmdeviceapi.h>  // Multimedia Device API for audio endpoint devices
#pragma comment(lib, "ws2_32.lib")  // Link with Winsock library
#pragma comment(lib, "ole32.lib")   // Link with Object Linking and Embedding
#pragma comment(lib, "winmm.lib")   // Windows multimedia library
#endif

using namespace std;

#define FRAME_DELAY 100

// Function to initialize audio capture from the default microphone
bool initializeAudioCapture(IAudioCaptureClient** pCaptureClient, IAudioClient** pAudioClient) {
    // Initialize COM library for use by the calling thread, set to multi-threaded environment
    CoInitialize(nullptr);

    // Declare device enumerator for capturing multimedia device interfaces
    IMMDeviceEnumerator* deviceEnumerator = nullptr;
    HRESULT hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_ALL,
        __uuidof(IMMDeviceEnumerator), (void**)&deviceEnumerator);
    if (FAILED(hr)) {
        cerr << "Failed to create device enumerator, HRESULT: " << hr << endl;
        return false;
    }

    // Declare the audio device interface
    IMMDevice* device = nullptr;
    // Get the default audio capture endpoint
    hr = deviceEnumerator->GetDefaultAudioEndpoint(eCapture, eConsole, &device);
    if (FAILED(hr)) {
        cerr << "Failed to get default audio endpoint, HRESULT: " << hr << endl;
        return false;
    }

    // Activate the audio client interface on the device
    hr = device->Activate(__uuidof(IAudioClient), CLSCTX_ALL, nullptr, (void**)pAudioClient);
    if (FAILED(hr)) {
        cerr << "Failed to activate audio client, HRESULT: " << hr << endl;
        return false;
    }

    // Declare the format as a pointer to WAVEFORMATEX structure
    WAVEFORMATEX* waveFormat = nullptr;
    // Get the format that the audio engine uses internally to process digital audio data
    hr = (*pAudioClient)->GetMixFormat(&waveFormat);
    if (FAILED(hr)) {
        cerr << "Failed to get mix format, HRESULT: " << hr << endl;
        return false;
    }

    // Initialize the audio stream between the client and the audio engine
    hr = (*pAudioClient)->Initialize(AUDCLNT_SHAREMODE_SHARED, 0, 0, 0, waveFormat, nullptr);
    if (FAILED(hr)) {
        cerr << "Failed to initialize audio client, HRESULT: " << hr << endl;
        return false;
    }

    // Obtain the interface for audio capture client
    hr = (*pAudioClient)->GetService(__uuidof(IAudioCaptureClient), (void**)pCaptureClient);
    if (FAILED(hr)) {
        cerr << "Failed to get audio capture client, HRESULT: " << hr << endl;
        return false;
    }

    // Free the memory allocated for the mix format structure
    CoTaskMemFree(waveFormat);
    // Start the audio stream
    (*pAudioClient)->Start();
    return true;
}

// Function to calculate the volume from audio data
double calculateVolume(const BYTE* data, size_t numFrames, WORD numChannels, WORD bitsPerSample) {
    double rms = 0.0;  // Initialize Root Mean Square value
    // Check bits per sample to handle different audio formats
    if (bitsPerSample == 32) {
        // Cast byte pointer to 32-bit integer pointer
        const int32_t* sampleData = reinterpret_cast<const int32_t*>(data);
        // Iterate over all samples to compute the volume
        for (size_t i = 0; i < numFrames * numChannels; i++) {
            // Normalize sample value to [-1,1] range for 32-bit data
            double normalizedSample = sampleData[i] / static_cast<double>(INT32_MAX);
            rms += normalizedSample * normalizedSample;  // Sum squares of normalized samples
        }
    }
    else if (bitsPerSample == 16) {
        // Cast byte pointer to 16-bit integer pointer for 16-bit data
        const int16_t* sampleData = reinterpret_cast<const int16_t*>(data);
        for (size_t i = 0; i < numFrames * numChannels; i++) {
            // Normalize sample value to [-1,1] range for 16-bit data
            double normalizedSample = sampleData[i] / static_cast<double>(INT16_MAX);
            rms += normalizedSample * normalizedSample;  // Sum squares of normalized samples
        }
    }
    // Calculate the root mean square of the sum of squares, convert to percentage
    rms = (sqrt(rms / (numFrames * numChannels)) - 0.44)/0.07;
    return rms * 100.0;
}

// Main function to run the capture and processing loop
int main() {
    // Initialize Winsock
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    // Create socket for sending data over TCP
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        cerr << "Can't create socket, Err #" << WSAGetLastError() << endl;
        return 1;
    }

    // Server address configuration
    string ipAddress = "127.0.0.1";  // Localhost
    int port = 1989;  // Port number
    sockaddr_in hint;
    hint.sin_family = AF_INET;  // IPv4
    hint.sin_port = htons(port);  // Host to network short for port
    inet_pton(AF_INET, ipAddress.c_str(), &hint.sin_addr);  // Convert IP string to byte array

    // Connect to server
    if (connect(sock, (sockaddr*)&hint, sizeof(hint)) == SOCKET_ERROR) {
        cerr << "Can't connect, Err #" << WSAGetLastError() << endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    // Initialize audio capture and streaming
    IAudioCaptureClient* captureClient = nullptr;
    IAudioClient* audioClient = nullptr;
    if (!initializeAudioCapture(&captureClient, &audioClient)) {
        cerr << "Initialization failed." << endl;
        return 1;
    }

    // Get and print audio format details
    WAVEFORMATEX* format = nullptr;
    audioClient->GetMixFormat(&format);
    cout << "Audio format details:" << endl;
    cout << "Channels: " << format->nChannels << endl;
    cout << "Sample Rate: " << format->nSamplesPerSec << endl;
    cout << "Bits Per Sample: " << format->wBitsPerSample << endl;

    // Main loop to capture audio and send volume data
    while (true) {
        BYTE* pData = nullptr;
        UINT32 numFramesAvailable = 0;
        DWORD flags = 0;
        HRESULT hr = captureClient->GetBuffer(&pData, &numFramesAvailable, &flags, nullptr, nullptr);
        if (SUCCEEDED(hr) && numFramesAvailable > 0) {
            float volume = (float)calculateVolume(pData, numFramesAvailable, format->nChannels, format->wBitsPerSample);
            cout << "Volume: " << volume << "%" << endl;  // Output the volume as a percentage
            // Send volume data to the server
            int sendRes = send(sock, reinterpret_cast<char*>(&volume), sizeof(volume), 0);
            if (sendRes == SOCKET_ERROR) {
                cerr << "Could not send volume to server! Err #" << WSAGetLastError() << endl;
                break;
            }
        }
        else if (FAILED(hr)) {
            cerr << "Failed to get buffer, HRESULT: " << hr << endl;
        }
        // Release the buffer to prepare for next capture
        captureClient->ReleaseBuffer(numFramesAvailable);
        this_thread::sleep_for(chrono::milliseconds(FRAME_DELAY)); // Sleep to reduce CPU usage
    }

    // Cleanup resources
    CoTaskMemFree(format);  // Free the memory for the format
    closesocket(sock);  // Close the socket
    WSACleanup();  // Cleanup Winsock
    return 0;
}