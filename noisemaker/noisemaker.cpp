#include <iostream>
#include <string>
#include <cstring>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <ctime>
#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")  // Link with Winsock library
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
#endif

using namespace std;

int main() {
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
    cout << "initializing socket" << endl;
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        std::cerr << "Can't create socket, Err #" << WSAGetLastError() << std::endl;
        return 1;
    }

    int port = 1989;
    std::string ipAddress = "127.0.0.1";

    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(port);
    inet_pton(AF_INET, ipAddress.c_str(), &hint.sin_addr);

    cout << "connecting to server" << endl;

    int connectRes = connect(sock, (sockaddr*)&hint, sizeof(hint));
    if (connectRes == SOCKET_ERROR) {
        std::cerr << "Can't connect, Err #" << WSAGetLastError() << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    cout << "connected to server" << endl;


    while (true) {
        struct tm newtime;
        time_t now = time(0);
        localtime_s(&newtime, &now);

        int valueToSend = (newtime.tm_sec * (newtime.tm_min*60));
        int sendRes = send(sock, reinterpret_cast<char*>(&valueToSend), sizeof(valueToSend), 0);
        if (sendRes == SOCKET_ERROR) {
            cout << "Could not send to server! Err #" << WSAGetLastError() << "\r\n";
            break;
        }

        this_thread::sleep_for(chrono::milliseconds(1000));  // Send every 1000 ms
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}

/*
* 
    char buf[4096];
    std::string userInput;
    std::cout << "> ";
    getline(std::cin, userInput);

    int sendRes = send(sock, userInput.c_str(), userInput.size() + 1, 0);
    if (sendRes == SOCKET_ERROR) {
        std::cout << "Could not send to server! Err #" << WSAGetLastError() << "\r\n";
        continue;
    }
memset(buf, 0, 4096);
int bytesReceived = recv(sock, buf, 4096, 0);
if (bytesReceived == SOCKET_ERROR) {
    std::cout << "There was an error getting response from server\r\n";
}
else if (bytesReceived > 0) {
    std::cout << "SERVER> " << std::string(buf, bytesReceived) << "\r\n";
}
*/