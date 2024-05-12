#include <SDL.h>
#include <iostream>
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

vector<uint32_t> pixels(16 * 9, 0);  // Example for a 16x9 pixel screen
mutex pixelsMutex;
bool running = true;

void handleClient(SOCKET clientSocket) {
    std::cout << "Handling new client" << std::endl;
    uint32_t color;
    static size_t currentIndex = 0;  // Static index to keep track of the current pixel to update
    while (running) {
        int bytesReceived = recv(clientSocket, (char*)&color, sizeof(color), 0);
        if (bytesReceived == 0 || bytesReceived == -1) {
            break;
        }

        std::lock_guard<std::mutex> guard(pixelsMutex);
        // Update only one pixel at a time
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
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 640, 360, 0);  // Adjusted size for better visibility
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_Texture* texture = SDL_CreateTexture(renderer,
        SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STATIC, 16, 9);

    SDL_Event event;
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            }
        }

        {
            std::lock_guard<std::mutex> guard(pixelsMutex);
            SDL_UpdateTexture(texture, NULL, pixels.data(), 16 * sizeof(uint32_t));  // Correct pitch for 16 pixels wide
        }

        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, NULL, NULL);
        SDL_RenderPresent(renderer);
        SDL_Delay(1000);  // Approximately 60 fps
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