#include <SDL.h>
#include <iostream>
#include <bitset>
#include <sstream>
#include <thread>
#include <mutex>
#include <vector>
#include <cstring>
#include <cstdlib>
#include <glew.h>
#include <glfw3.h>

#ifdef _WIN32
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")  // Ensure linker includes Winsock library
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#endif

using namespace std;

#define FRAME_DELAY 16
#define PIXEL_WIDTH 1184
#define PIXEL_HEIGHT 666
#define PIXEL_COUNT ((PIXEL_WIDTH/10) * (PIXEL_HEIGHT/10))

vector<uint32_t> pixels(PIXEL_COUNT, 0);  // Example for a 16x9 pixel screen
mutex pixelsMutex;
bool running = true;
double d_cur = 0.0;
double d_prev = 0.0;

// Camera position and direction
float camX = -0.0f,
camY = 66.0f,
camZ = -50.0f;
float camYaw = -3.14159265358979323846264338f,
camPitch = 3.14159265358979323846264338f;

// -30.5    82      -3.8147e-06
float lightX = -30.5f,
lightY = 82.0f,
lightZ = 0.0f;
const float speed = 0.1f; // Movement speed
const float sensitivity = 0.0005f; // Mouse sensitivity

// Light position
GLfloat lightPos[] = { -0.0f, 66.0f, -50.0f, 1.0f };

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

        r = hue2rgb(p, q, hue + 1.0f / 3);
        g = hue2rgb(p, q, hue);
        b = hue2rgb(p, q, hue - 1.0f / 3);
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
        //std::cout << std::bitset<32>(audioData).to_string() << std::endl;

        uint8_t frequencyByte = (uint8_t)(audioData >> 8);
        //std::cout << "freq: " << std::bitset<8>(frequencyByte).to_string() << std::endl;

        // Determine the hue index
        int hueIndex = frequencyByte / 16;

        // Convert the hue to RGB with constant saturation and lightness
        float saturation = 1.0f;  // Full saturation
        float lightness = 0.5f;   // Medium lightness

        uint32_t frequencyColor = HSLtoRGB(hues[hueIndex], saturation, lightness);

        //cout << "frequencyColor: " << std::bitset<32>(frequencyColor).to_string() << std::endl;

        //uint8_t colorByte = (uint8_t)((color >> 24) & 0x000000FF);
        uint8_t volumeByte = (uint8_t)audioData;
        //std::cout << std::bitset<8>(volumeByte).to_string() << std::endl;
        volumeByte &= 224;
        volumeByte |= volumeByte >> 3;
        //std::cout << std::bitset<8>(volumeByte).to_string() << std::endl;

        uint32_t color = 0xFF000000 + (((uint32_t)volumeByte) << 16) + (((uint32_t)volumeByte) << 8) + ((uint32_t)volumeByte);
        //std::cout << std::bitset<32>(color).to_string() << std::endl;
        //std::cout << std::bitset<32>(frequencyColor).to_string() << std::endl;
        color &= frequencyColor;
        //std::cout << std::bitset<32>(color).to_string() << std::endl;
        color &= 4293980400; //11111111 11110000 11110000 11110000
        //cout << "--------" << endl;

        std::lock_guard<std::mutex> guard(pixelsMutex);
        // Update only one pixel at a time

        // Xbox headset mic:
        // double volume = ((double)color - 1103250000.0) / 22420000.0;

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

void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    glViewport(0, 0, width, height);
}

void setPerspective(float fov, float aspect, float f_near, float f_far) {
    float f = 1.0f / tanf(fov * (3.14159265358979323846f / 180.0f) / 2.0f);
    float depth = f_near - f_far;

    float perspective[16] = {
        f / aspect, 0, 0, 0,
        0, f, 0, 0,
        0, 0, (f_far + f_near) / depth, -1,
        0, 0, (2 * f_far * f_near) / depth, 0
    };

    glMatrixMode(GL_PROJECTION);
    glLoadMatrixf(perspective);
    glMatrixMode(GL_MODELVIEW);
}

// Function to handle keyboard input
void processInput(GLFWwindow* window) {
    float _lightX = lightX;
    float _lightY = lightY;
    float _lightZ = lightZ;

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
        lightX += speed * sin(camYaw);
        lightZ += speed * cos(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
        lightX -= speed * sin(camYaw);
        lightZ -= speed * cos(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
        lightX -= speed * cos(camYaw);
        lightZ += speed * sin(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
        lightX += speed * cos(camYaw);
        lightZ -= speed * sin(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS) {
        lightY += speed;
    }
    if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS) {
        lightY -= speed;
    }

    if (lightX != _lightX || lightY != _lightY || lightZ != _lightZ) {
        cout << "-> lightX: " << lightX << endl;
        cout << "-> lightY: " << lightY << endl;
        cout << "-> lightZ: " << lightZ << endl;
    }

    // Update the light position array
    lightPos[0] = lightX;
    lightPos[1] = lightY;
    lightPos[2] = lightZ;
}

// Mouse callback function
void mouseCallback(GLFWwindow* window, double xpos, double ypos) {
    static double lastX = xpos, lastY = ypos;
    double xoffset = xpos - lastX;
    double yoffset = lastY - ypos; // Reversed since y-coordinates range from bottom to top
    lastX = xpos;
    lastY = ypos;

    xoffset *= sensitivity;
    yoffset *= sensitivity;

    camYaw += xoffset;
    camPitch += yoffset;

    if (camPitch > 89.0f) camPitch = 89.0f;
    if (camPitch < -89.0f) camPitch = -89.0f;

    cout << "camYaw: " << camYaw << endl;
    cout << "camPitch: " << camPitch << endl;
    cout << "///" << endl;
}

// Function to create a lookAt matrix
void lookAt(float eyeX, float eyeY, float eyeZ, float centerX, float centerY, float centerZ, float upX, float upY, float upZ) {
    float forwardX = centerX - eyeX;
    float forwardY = centerY - eyeY;
    float forwardZ = centerZ - eyeZ;

    // Normalize forward vector
    float forwardMag = sqrt(forwardX * forwardX + forwardY * forwardY + forwardZ * forwardZ);
    forwardX /= forwardMag;
    forwardY /= forwardMag;
    forwardZ /= forwardMag;

    // Compute the right vector
    float rightX = forwardY * upZ - forwardZ * upY;
    float rightY = forwardZ * upX - forwardX * upZ;
    float rightZ = forwardX * upY - forwardY * upX;

    // Normalize right vector
    float rightMag = sqrt(rightX * rightX + rightY * rightY + rightZ * rightZ);
    rightX /= rightMag;
    rightY /= rightMag;
    rightZ /= rightMag;

    // Compute the up vector
    float upnX = rightY * forwardZ - rightZ * forwardY;
    float upnY = rightZ * forwardX - rightX * forwardZ;
    float upnZ = rightX * forwardY - rightY * forwardX;

    float viewMatrix[16] = {
        rightX,    upnX,    -forwardX,   0.0f,
        rightY,    upnY,    -forwardY,   0.0f,
        rightZ,    upnZ,    -forwardZ,   0.0f,
        0.0f,      0.0f,    0.0f,        1.0f
    };

    // cout << "camera: " << eyeX << "\t" << eyeY << "\t" << eyeZ << endl;

    glMultMatrixf(viewMatrix);
    glTranslatef(-eyeX, -eyeY, -eyeZ);
}

void setupLighting() {
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);

    GLfloat ambientLight[] = { 1.0f, 1.0f, 1.0f, 1.0f };
    // GLfloat diffuseLight[] = { 0.9f, 0.9f, 0.9f, 1.0f };
    // GLfloat specularLight[] = { 1.0f, 1.0f, 1.0f, 1.0f };
    GLfloat lightPosition[] = { 1.0f, 1.0f, 1.0f, 0.0f }; // Directional light

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight);
    // glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight);
    // glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight);
    glLightfv(GL_LIGHT0, GL_POSITION, lightPosition);

    glEnable(GL_COLOR_MATERIAL);
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);
}

void setupMaterial() {
    GLfloat mat_specular[] = { 1.0f, 1.0f, 1.0f, 1.0f };
    GLfloat mat_shininess[] = { 50.0f };

    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular);
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess);
}

void drawCube(float x, float y, float z, float size, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    float half_size = size / 2;
    glColor3ub(r, g, b);

    // Calculate brightness as the average of the RGB values
    float brightness = (r + g + b) / (765.0f);

    // Use brightness to scale the z-axis size
    float zScale = 1.0f + brightness * 50.0f; // Example: elongate by up to 2 times the original size
    float half_size_times_zScale = half_size * zScale;

    /*
    if (r + g + b > 0) {
        cout << "cube: (" << x << "\t" << y << "\t" << z << ") - zScale: " << zScale << endl;
    }
    */

    glBegin(GL_QUADS);

    float x_m_hs = x - half_size;
    float x_p_hs = x + half_size;
    float y_m_hs = y - half_size;
    float y_p_hs = y + half_size;
    float topZ = z + half_size_times_zScale;
    float botZ = z - half_size_times_zScale;

    // Front face
    glVertex3f(x_m_hs, y_m_hs, topZ);
    glVertex3f(x_p_hs, y_m_hs, topZ);
    glVertex3f(x_p_hs, y_p_hs, topZ);
    glVertex3f(x_m_hs, y_p_hs, topZ);

    // Back face
    glVertex3f(x_m_hs, y_m_hs, botZ);
    glVertex3f(x_m_hs, y_p_hs, botZ);
    glVertex3f(x_p_hs, y_p_hs, botZ);
    glVertex3f(x_p_hs, y_m_hs, botZ);

    // Top face
    glVertex3f(x_m_hs, y_p_hs, botZ);
    glVertex3f(x_m_hs, y_p_hs, topZ);
    glVertex3f(x_p_hs, y_p_hs, topZ);
    glVertex3f(x_p_hs, y_p_hs, botZ);

    // Bottom face
    glVertex3f(x_m_hs, y_m_hs, botZ);
    glVertex3f(x_p_hs, y_m_hs, botZ);
    glVertex3f(x_p_hs, y_m_hs, topZ);
    glVertex3f(x_m_hs, y_m_hs, topZ);

    // Right face
    glVertex3f(x_p_hs, y_m_hs, botZ);
    glVertex3f(x_p_hs, y_p_hs, botZ);
    glVertex3f(x_p_hs, y_p_hs, topZ);
    glVertex3f(x_p_hs, y_m_hs, topZ);

    // Left face
    glVertex3f(x_m_hs, y_m_hs, botZ);
    glVertex3f(x_m_hs, y_m_hs, topZ);
    glVertex3f(x_m_hs, y_p_hs, topZ);
    glVertex3f(x_m_hs, y_p_hs, botZ);

    glEnd();
}

void drawLightSource() {
      // glPushMatrix();
      // glTranslatef(lightX, lightY, lightZ);
      // glColor3f(1.0f, 1.0f, 1.0f); // White color
    drawCube(lightX, lightY, lightZ, 0.5f, 0xFF, 0x0, 0x0, 0xFF);
      // glPopMatrix();
}

int graphicsThread(int argc, char* argv[]) {
    if (!glfwInit()) {
        return -1;
    }

    GLFWwindow* window = glfwCreateWindow(PIXEL_WIDTH, PIXEL_HEIGHT, "Pixels", NULL, NULL);
    if (!window) {
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    if (glewInit() != GLEW_OK) {
        return -1;
    }

    // Set up camera
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    setPerspective(45.0f, (float)PIXEL_WIDTH / (float)PIXEL_HEIGHT, 0.1f, 1000.0f);

    setupLighting(); // Setup lighting
    setupMaterial(); // Setup material properties

    // Set mouse callback
    // glfwSetCursorPosCallback(window, mouseCallback);
    // glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED); // Hide the cursor and capture it

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        processInput(window); // Process keyboard input

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glLoadIdentity();

        // Calculate camera direction
        float camDirX = cos(camPitch) * sin(camYaw);
        float camDirY = sin(camPitch);
        float camDirZ = cos(camPitch) * cos(camYaw);

        // Apply the camera transformation
        lookAt(camX, camY, camZ, camX + camDirX, camY + camDirY, camZ + camDirZ, 0.0f, 1.0f, 0.0f);

        // Set light position after setting the camera
        // glLightfv(GL_LIGHT0, GL_POSITION, lightPos);

        // Draw the light source as an extended red cube
        // drawLightSource();

        std::lock_guard<std::mutex> guard(pixelsMutex);

        float cubeSize = 0.5f; // Adjust cube size for better visibility
        for (int y = 0; y < PIXEL_HEIGHT / 10; ++y) {
            for (int x = 0; x < (PIXEL_WIDTH / 10); ++x) {
                int index = y * (PIXEL_WIDTH / 10) + x;
                uint32_t color = pixels[index];
                uint8_t a = (color >> 24) & 0xFF;
                uint8_t r = (color >> 16) & 0xFF;
                uint8_t g = (color >> 8) & 0xFF;
                uint8_t b = color & 0xFF;
                drawCube(x * cubeSize - ((PIXEL_WIDTH / 10) * cubeSize / 2),
                    (((PIXEL_HEIGHT / 2) - 1) - y) * cubeSize - ((PIXEL_HEIGHT / 2) * cubeSize / 2),
                    0.0f, cubeSize, r, g, b, a);
            }
        }

        glfwSwapBuffers(window);
        glfwWaitEventsTimeout(FRAME_DELAY / 1000.0);
    }

    glfwDestroyWindow(window);
    glfwTerminate();

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
