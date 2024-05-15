#include <SDL.h>
#include <iostream>
#include <bitset>
#include <sstream>
#include <thread>
#include <mutex>
#include <vector>
#include <cstring>
#include <cstdlib>
#ifdef _WIN32
    #include <winsock2.h>
    #pragma comment(lib, "ws2_32.lib")  // Ensure linker includes Winsock library
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <unistd.h>
#endif

using namespace std;

#define FRAME_DELAY 60
#define PIXEL_WIDTH 160
#define PIXEL_HEIGHT 90
#define PIXEL_COUNT (PIXEL_WIDTH * PIXEL_HEIGHT)

vector<uint32_t> pixels(PIXEL_COUNT, 0);  // Example for a 16x9 pixel screen
mutex pixelsMutex;
bool running = true;
double d_cur = 0.0;
double d_prev = 0.0;

void receiveUint32(SOCKET clientSocket, uint32_t& value) {
    char buffer[sizeof(uint32_t)];
    int bytesReceived = recv(clientSocket, buffer, sizeof(buffer), 0); // Receive the serialized data

    if (bytesReceived == sizeof(uint32_t)) {
        memcpy(&value, buffer, sizeof(uint32_t)); // Deserialize the data into a uint32_t
    }
    else {
        std::cerr << "Failed to receive uint32_t\n";
    }
}

// Function to convert HSL to RGB
unsigned int HSLtoRGB(float hue, float saturation, float lightness) {
    float r, g, b;

    if (saturation == 0) {
        r = g = b = lightness; // achromatic
    }
    else {
        auto hue2rgb = [](float p, float q, float t) {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1.0f / 6) return p + (q - p) * 6 * t;
            if (t < 1.0f / 2) return q;
            if (t < 2.0f / 3) return p + (q - p) * (2.0f / 3 - t) * 6;
            return p;
            };

        float q = lightness < 0.5 ? lightness * (1 + saturation) : lightness + saturation - lightness * saturation;
        float p = 2 * lightness - q;

        r = hue2rgb(p, q, hue + 1.0 / 3);
        g = hue2rgb(p, q, hue);
        b = hue2rgb(p, q, hue - 1.0 / 3);
    }

    unsigned int R = static_cast<unsigned int>(r * 255);
    unsigned int G = static_cast<unsigned int>(g * 255);
    unsigned int B = static_cast<unsigned int>(b * 255);

    return 0xFF000000 | (R << 16) | (G << 8) | B;
}

// 16 hues representing a full rainbow
float hues[16] = {
    0.0f / 16, 1.0f / 16, 2.0f / 16, 3.0f / 16,
    4.0f / 16, 5.0f / 16, 6.0f / 16, 7.0f / 16,
    8.0f / 16, 9.0f / 16, 10.0f / 16, 11.0f / 16,
    12.0f / 16, 13.0f / 16, 14.0f / 16, 15.0f / 16
};

void handleClient(SOCKET clientSocket) {
    std::cout << "Handling new client" << std::endl;
    static size_t currentIndex = 0;  // Static index to keep track of the current pixel to update

    while (running) {
        uint32_t audioData;
        receiveUint32(clientSocket, audioData);
        std::cout << std::bitset<32>(audioData).to_string() << std::endl;

        uint8_t frequencyByte = (uint8_t)(audioData >> 8);
        std::cout << "freq: " << std::bitset<8>(frequencyByte).to_string() << std::endl;

        // Determine the hue index
        int hueIndex = frequencyByte / 16;

        // Convert the hue to RGB with constant saturation and lightness
        float saturation = 1.0f;  // Full saturation
        float lightness = 0.5f;   // Medium lightness

        uint32_t frequencyColor = HSLtoRGB(hues[hueIndex], saturation, lightness);

        cout << "frequencyColor: " << std::bitset<32>(frequencyColor).to_string() << std::endl;

        //uint8_t colorByte = (uint8_t)((color >> 24) & 0x000000FF);
        uint8_t volumeByte = (uint8_t)audioData;
        std::cout << std::bitset<8>(volumeByte).to_string() << std::endl;
        volumeByte &= 224;
        volumeByte |= volumeByte >> 3;
        std::cout << std::bitset<8>(volumeByte).to_string() << std::endl;

        uint32_t color = 0xFF000000 + (((uint32_t)volumeByte) << 16) + (((uint32_t)volumeByte) << 8) + ((uint32_t)volumeByte);
        std::cout << std::bitset<32>(color).to_string() << std::endl;
        std::cout << std::bitset<32>(frequencyColor).to_string() << std::endl;
        color &= frequencyColor;
        std::cout << std::bitset<32>(color).to_string() << std::endl;
        cout << "--------" << endl;

        //char* converted = (char*)"";
        //sscanf_s(converted, "%hhu", &)
        //cout << bitset<32>(color).to_string() << endl;

        std::lock_guard<std::mutex> guard(pixelsMutex);
        // Update only one pixel at a time
        
        // Xbox headset mic:
        // double volume = ((double)color - 1103250000.0) / 22420000.0;
        
        /*
        double volume = ((double)color) / 100.0;
        cout << "[" << volume << "]" << endl;
        cout << "[" << bitset<32>((UINT32)volume).to_string() << "]" << endl;
        //double colorValue = ((double)color);
        
        
        // UINT32 argb = (int)(colorValue * (double)0xFFFFFFFF);
        // UINT8 a = 255 - ((argb & 0xFF000000) >> 24);
        // UINT8 r = 255 - ((argb & 0x00FF0000) >> 16);
        // UINT8 g = 255 - ((argb & 0x0000FF00) >> 8);
        /// UINT8 b = 255 - ((argb & 0x000000FF));
        // UINT8 selectedValue = ((UINT32)r + (UINT32)g + (UINT32)b) / 3; //average

        cout << "volume: " << volume << endl;
        double brightness = (volume * (double)0xFFFFFFFF);
        cout << "brightness: " << bitset<32>((UINT32)brightness).to_string() << endl;
        // UINT8 selectedValue = (UINT8)(((UINT32)brightness >> 24) & 0x000000FF);
        // cout << "brightness uint8: " << bitset<8>(selectedValue).to_string() << endl;

        d_cur = brightness;

        cout << "d_prev: " << bitset<32>((UINT32)d_cur).to_string() << endl;
        cout << "d_cur: " << bitset<32>((UINT32)d_prev).to_string() << endl;
        
        d_prev = d_cur;
        
        UINT32 color = 0xFF000000 + (((UINT32)colorByte) << 16) + (((UINT32)colorByte) << 8) + ((UINT32)colorByte);

        //auto res = (std::stringstream{} << std::hex << (int)(colorValue * (double)0xFFFFFFFF)).str();
        //cout << bitset<32>(argb).to_string() << endl;
        //cout << bitset<8>(a).to_string() << endl;
        //cout << bitset<8>(r).to_string() << endl;
        //cout << bitset<8>(g).to_string() << endl;
        //cout << bitset<8>(b).to_string() << endl;
        cout << "color uint8:  " << bitset<8>(colorByte).to_string() << endl;
        cout << "color uint32: " << bitset<32>(color).to_string() << endl;
        std::cout << "============" << endl;
        */


        pixels[currentIndex] = color;
        
        // Increment the index and wrap around if necessary
        currentIndex = (currentIndex + 1) % pixels.size();
    }
#ifdef _WIN32
    closesocket(clientSocket);
#else
    close(clientSocket);
#endif
}


int graphicsThread(int argc, char* argv[]) {
    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window* window = SDL_CreateWindow("Pixels",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, PIXEL_WIDTH, PIXEL_HEIGHT, 0);  // Adjusted size for better visibility
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_Texture* texture = SDL_CreateTexture(renderer,
        SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STATIC, PIXEL_WIDTH, PIXEL_HEIGHT);

    SDL_Event event;
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            }
        }

        {
            std::lock_guard<std::mutex> guard(pixelsMutex);
            SDL_UpdateTexture(texture, NULL, pixels.data(), PIXEL_WIDTH * sizeof(uint32_t));  // Correct pitch for 16 pixels wide
        }

        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, NULL, NULL);
        SDL_RenderPresent(renderer);
        SDL_Delay(FRAME_DELAY);
    }

    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}


int main(int argc, char* argv[]) {
    std::thread gThread(graphicsThread, argc, argv);
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
    cout << "initializing server socket" << endl;
    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, 0);  // Use SOCKET type for Windows
    if (serverSocket == INVALID_SOCKET) {
        std::cerr << "Can't create a socket!";
        return 1;
    }

    sockaddr_in serverHint;
    serverHint.sin_family = AF_INET;
    serverHint.sin_port = htons(1989);
    serverHint.sin_addr.s_addr = INADDR_ANY;

    cout << "binding" << endl;
    if (bind(serverSocket, (sockaddr*)&serverHint, sizeof(serverHint)) == SOCKET_ERROR) {
        cerr << "Bind failed with error: " << WSAGetLastError() << endl;
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }

    cout << "listening" << endl;
    if (listen(serverSocket, SOMAXCONN) == SOCKET_ERROR) {
        cerr << "Listen failed with error: " << WSAGetLastError() << endl;
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }

    sockaddr_in client;
    int clientSize = sizeof(client);  // Change type to int for Windows

    while (true) {
        cout << "ready to accept clients" << endl;
        SOCKET clientSocket = accept(serverSocket, (sockaddr*)&client, &clientSize);  // Cast may be required here if warning persists
        cout << "accepted client connection" << endl;
        std::thread clientThread(handleClient, clientSocket);
        cout << "initialized client thread" << endl;
        clientThread.detach();
        cout << "client thread detached" << endl;
    }
#ifdef _WIN32
    WSACleanup();
#endif
    gThread.join();
    return 0;
}