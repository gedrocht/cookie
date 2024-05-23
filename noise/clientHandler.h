#pragma once

#ifdef _WIN32

#ifdef APIENTRY
#undef APIENTRY
#endif
#include <winsock2.h>           // For Windows-specific socket operations
#pragma comment(lib, "ws2_32.lib") // Link with the Windows Sockets library
#else
#include <sys/socket.h>         // For Unix/Linux socket operations
#include <netinet/in.h>         // For internet address family
#include <unistd.h>             // For POSIX operating system API
#endif

#include <stdint.h>
#include <iostream>
#include <thread>               // For multithreading support
#include <mutex>                // For mutual exclusion to prevent race conditions
#include <vector>

#include "block.h"
#include "colorHandler.h"

template <typename T>
class ClientHandler {
public:
    SOCKET* clientSocket;

    mutex* dataLock;

    vector<T*>* items;
    ClientHandler();
    ClientHandler(mutex* lock, vector<T*>* items, int barsCount, int* currentIndex, int* numClients);
    int initialize();

    bool running;

    int* numClients;
    int* currentIndex;
    int barsCount;

    // Function to receive a uint32_t value over a socket
    static bool receiveUint32(SOCKET clientSocket, uint32_t& value);

    // Function to handle client connections and update pixel data
    static void handleClient(ClientHandler* clientHandler);
};


// Function to receive a uint32_t value over a socket
template <typename T>
bool ClientHandler<T>::receiveUint32(SOCKET clientSocket, uint32_t& value) {
    char buffer[sizeof(uint32_t)];
    int bytesReceived = recv(clientSocket, buffer, sizeof(buffer), 0);

    if (bytesReceived == sizeof(uint32_t)) {
        memcpy(&value, buffer, sizeof(uint32_t));
        return true;
    }
    else {
        // cerr << "Failed to receive uint32_t\n";
        return false;
    }
}

template <typename T>
// Function to handle client connections and update pixel data
void ClientHandler<T>::handleClient(ClientHandler<T>* clientHandler) {
    cout << "Handling new client" << endl;

    (*clientHandler->numClients)++;
    while (clientHandler->running) {
        uint32_t audioData;
        if (!receiveUint32(*clientHandler->clientSocket, audioData)) {
            (*clientHandler->numClients)--;
            break;
        }

        uint32_t color = 0;
        try {
            color = ColorHandler::getColorFromData(audioData);
        }
        catch (exception& e) {
            if (*clientHandler->numClients > 1) {
                continue;
            }
        }

        // color &= 4293980400; // 11111111 11110000 11110000 11110000

        {
            std::lock_guard<std::mutex> guard(*clientHandler->dataLock);
            // Update only one pixel at a time
            clientHandler->items->at(*clientHandler->currentIndex)->setColor(
                (color >> 16) & 0xFF,
                (color >> 8) & 0xFF,
                color & 0xFF,
                (color >> 24) & 0xFF);
            // Increment the index and wrap around if necessary
            int newIndex = *clientHandler->currentIndex; 
            newIndex = (newIndex + 1) % (clientHandler->barsCount);
            *clientHandler->currentIndex = newIndex;
        }
    }

#ifdef _WIN32
    closesocket(*clientHandler->clientSocket);
#else
    close(*clientHandler->clientSocket);
#endif
}

template <typename T>
ClientHandler<T>::ClientHandler() {}

template <typename T>
ClientHandler<T>::ClientHandler(mutex* lock, vector<T*>* items, int barsCount, int* currentIndex, int* numClients) {
    this->numClients = numClients;
    (*this->numClients)++;
    this->barsCount = barsCount;
    this->dataLock = lock;
    this->items = items;
    this->barsCount = barsCount;
    this->currentIndex = currentIndex;
    this->numClients = numClients;
    this->running = true;
}

template <typename T>
int ClientHandler<T>::initialize() {

#ifdef _WIN32
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        fprintf(stderr, "WSAStartup failed with error: %d\n", result);
        exit(EXIT_FAILURE); // or return from the function if it is not the main function
    }
#endif

    cout << "initializing server socket" << endl;
    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == INVALID_SOCKET) {
        cerr << "Can't create a socket!";
        return 1;
    }

    sockaddr_in serverHint = {};
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

    sockaddr_in client = {};
    int clientSize = sizeof(client);

    while (true) {
        cout << "ready to accept clients" << endl;
        SOCKET cSocket = accept(serverSocket, (sockaddr*)&client, &clientSize);
        this->clientSocket = &cSocket;
        cout << "accepted client connection" << endl;
        thread clientThread(&ClientHandler::handleClient, this);
        cout << "initialized client thread" << endl;
        clientThread.detach();
        cout << "client thread detached" << endl;
    }

#ifdef _WIN32
    WSACleanup();
#endif
}
