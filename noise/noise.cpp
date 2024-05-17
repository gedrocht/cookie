#include <iostream>
#include <bitset>
#include <fstream>
#include <sstream>
#include <thread>
#include <mutex>
#include <vector>
#include <cstring>
#include <cstdlib>
#include <glew.h>
#include <glfw3.h>
#include <glm.hpp>
#define GLM_ENABLE_EXPERIMENTAL
#include <gtc/matrix_transform.hpp>
#include <gtc/type_ptr.hpp>
#include <gtx/string_cast.hpp>

#ifdef _WIN32
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#endif

using namespace std;

// Constants for window and shadow map dimensions
#define FRAME_DELAY 16
#define PIXEL_WIDTH 1184
#define PIXEL_HEIGHT 666
#define PIXEL_COUNT ((PIXEL_WIDTH/10) * (PIXEL_HEIGHT/10))
#define SHADOW_WIDTH 1024
#define SHADOW_HEIGHT 1024

// #define KEYBOARD_INPUT
// #define KEYBOARD_CONTROLS_CAMERA
// #define KEYBOARD_CONTROLS_LIGHT
// #define MOUSE_INPUT
#define ANTIALIASING

// Pixel data and synchronization
vector<uint32_t> pixels(PIXEL_COUNT, 0);
size_t currentIndex = 0;
mutex pixelsMutex;
bool running = true;

/*
* cam: 1.01008, 51.5, 61.6449
camYaw: 3.1435, camPitch: -1.63751
*/

// Camera position and direction
float camX = 0.0f, camY = 50.0f, camZ = 64.0f;
float camYaw = 3.143f, camPitch = -1.58;

// Constants for movement speed and mouse sensitivity
// Constants for movement speed and mouse sensitivity
const float speed = 0.25f;
const float sensitivity = 0.0005f;
float lightAngle = 0;
float lightDistance = 20.0f;
float lightSpeed = 0.0174533;

// Light position
glm::vec3 lightPos(-40.0f, 300.0f, 100.0f);

// Shader and framebuffer objects
GLuint depthMapFBO, depthMap;
#ifdef ANTIALIASING
GLuint fxaaFBO, texColorBuffer, fxaaShaderProgram;
#endif
GLuint depthShaderProgram, sceneShaderProgram;

// Uniform locations for shaders
GLint modelLoc, viewLoc, projectionLoc, lightPosLoc, viewPosLoc, lightSpaceMatrixLoc, yScaleLoc;

// Vertex data for a simple cube (positions and normals)
float vertices[] = {
    -0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
     0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
     0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
     0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    -0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    -0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,

    -0.5f, -0.5f,  0.5f,  0.0f,  0.0f,  1.0f,
     0.5f, -0.5f,  0.5f,  0.0f,  0.0f,  1.0f,
     0.5f,  0.5f,  0.5f,  0.0f,  0.0f,  1.0f,
     0.5f,  0.5f,  0.5f,  0.0f,  0.0f,  1.0f,
    -0.5f,  0.5f,  0.5f,  0.0f,  0.0f,  1.0f,
    -0.5f, -0.5f,  0.5f,  0.0f,  0.0f,  1.0f,

    -0.5f,  0.5f,  0.5f, -1.0f,  0.0f,  0.0f,
    -0.5f,  0.5f, -0.5f, -1.0f,  0.0f,  0.0f,
    -0.5f, -0.5f, -0.5f, -1.0f,  0.0f,  0.0f,
    -0.5f, -0.5f, -0.5f, -1.0f,  0.0f,  0.0f,
    -0.5f, -0.5f,  0.5f, -1.0f,  0.0f,  0.0f,
    -0.5f,  0.5f,  0.5f, -1.0f,  0.0f,  0.0f,

     0.5f,  0.5f,  0.5f,  1.0f,  0.0f,  0.0f,
     0.5f,  0.5f, -0.5f,  1.0f,  0.0f,  0.0f,
     0.5f, -0.5f, -0.5f,  1.0f,  0.0f,  0.0f,
     0.5f, -0.5f, -0.5f,  1.0f,  0.0f,  0.0f,
     0.5f, -0.5f,  0.5f,  1.0f,  0.0f,  0.0f,
     0.5f,  0.5f,  0.5f,  1.0f,  0.0f,  0.0f,

    -0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,
     0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,
     0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,
     0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,
    -0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,
    -0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,

    -0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f,
     0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f,
     0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,
     0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,
    -0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,
    -0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f
};

// VBO and VAO
unsigned int VBO, VAO;

// Function to receive a uint32_t value over a socket
void receiveUint32(SOCKET clientSocket, uint32_t& value) {
    char buffer[sizeof(uint32_t)];
    int bytesReceived = recv(clientSocket, buffer, sizeof(buffer), 0);

    if (bytesReceived == sizeof(uint32_t)) {
        memcpy(&value, buffer, sizeof(uint32_t));
    }
    else {
        cerr << "Failed to receive uint32_t\n";
    }
}

// Function to convert HSL to RGB
unsigned int HSLtoRGB(float hue, float saturation, float lightness) {
    float r, g, b;

    if (saturation == 0) {
        r = g = b = lightness;
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

// Array of 16 hues representing a full rainbow
float hues[16] = {
    0.0f / 16, 1.0f / 16, 2.0f / 16, 3.0f / 16,
    4.0f / 16, 5.0f / 16, 6.0f / 16, 7.0f / 16,
    8.0f / 16, 9.0f / 16, 10.0f / 16, 11.0f / 16,
    12.0f / 16, 13.0f / 16, 14.0f / 16, 15.0f / 16
};

// Function to handle client connections and update pixel data
void handleClient(SOCKET clientSocket) {
    cout << "Handling new client" << endl;

    while (running) {
        uint32_t audioData;
        receiveUint32(clientSocket, audioData);

        uint8_t frequencyByte = (uint8_t)(audioData >> 8);

        // Determine the hue index
        int hueIndex = frequencyByte / 16;

        // Convert the hue to RGB with constant saturation and lightness
        float saturation = 1.0f;
        float lightness = 0.5f;

        uint32_t frequencyColor = HSLtoRGB(hues[hueIndex], saturation, lightness);

        uint8_t volumeByte = (uint8_t)audioData;
        volumeByte &= 224;
        volumeByte |= volumeByte >> 3;

        uint32_t color = 0xFF000000 + (((uint32_t)volumeByte) << 16) + (((uint32_t)volumeByte) << 8) + ((uint32_t)volumeByte);
        color &= frequencyColor;
        color &= 4293980400; // 11111111 11110000 11110000 11110000

        lock_guard<mutex> guard(pixelsMutex);
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

// Function to handle window resize
void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    glViewport(0, 0, width, height);
}

#ifdef MOUSE_INPUT
void mouseCallback(GLFWwindow* window, double xpos, double ypos) {
    static double lastX = xpos, lastY = ypos;
    double xoffset = xpos - lastX;
    double yoffset = lastY - ypos; // Reversed since y-coordinates range from bottom to top
    lastX = xpos;
    lastY = ypos;

    xoffset *= sensitivity;
    yoffset *= sensitivity;

    camYaw -= xoffset;
    camPitch -= yoffset;

    cout << "camYaw: " << camYaw << ", camPitch: " << camPitch << endl;

    if (camPitch > 89.0f) camPitch = 89.0f;
    if (camPitch < -89.0f) camPitch = -89.0f;
}
#endif

// Function to handle keyboard input for camera movement
#ifdef KEYBOARD_INPUT
void processInput(GLFWwindow* window) {
#ifdef KEYBOARD_CONTROLS_LIGHT
    float _lightX = lightPos[0];
    float _lightY = lightPos[1];
    float _lightZ = lightPos[2];

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
        _lightX -= speed * sin(camYaw);
        _lightZ -= speed * cos(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
        _lightX += speed * sin(camYaw);
        _lightZ += speed * cos(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
        _lightX -= speed * cos(camYaw);
        _lightZ += speed * sin(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
        _lightX += speed * cos(camYaw);
        _lightZ -= speed * sin(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS) {
        _lightY += speed;
    }
    if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS) {
        _lightY -= speed;
    }

    if (_lightX != lightPos[0] || _lightY != lightPos[1] || _lightZ != lightPos[2]) {
        lightPos[0] = _lightX;
        lightPos[1] = _lightY;
        lightPos[2] = _lightZ;
        cout << "light: " << _lightX << ", " << _lightY << ", " << _lightZ << endl;
    }
#endif
#ifdef KEYBOARD_CONTROLS_CAMERA
    float _camX = camX;
    float _camY = camY;
    float _camZ = camZ;

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
        camX -= speed * sin(camYaw);
        camZ -= speed * cos(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
        camX += speed * sin(camYaw);
        camZ += speed * cos(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
        camX -= speed * cos(camYaw);
        camZ += speed * sin(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
        camX += speed * cos(camYaw);
        camZ -= speed * sin(camYaw);
    }
    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS) {
        camY += speed;
    }
    if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS) {
        camY -= speed;
    }

    if (camX != _camX || camY != _camY || camZ != _camZ) {
        cout << "cam: " << camX << ", " << camY << ", " << camZ << endl;
    }
#endif
}
#endif

// Function to compile a shader from source code
GLuint compileShader(const char* source, GLenum type) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, NULL);
    glCompileShader(shader);

    int success;
    char infoLog[512];
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(shader, 512, NULL, infoLog);
        cerr << "ERROR::SHADER::COMPILATION_FAILED\n" << infoLog << endl;
    }
    return shader;
}

// Function to link shaders into a program
GLuint linkProgram(GLuint vertexShader, GLuint fragmentShader) {
    GLuint program = glCreateProgram();
    glAttachShader(program, vertexShader);
    glAttachShader(program, fragmentShader);
    glLinkProgram(program);

    int success;
    char infoLog[512];
    glGetProgramiv(program, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(program, 512, NULL, infoLog);
        cerr << "ERROR::PROGRAM::LINKING_FAILED\n" << infoLog << endl;
    }
    return program;
}

// Function to read shader source code from a file
string readFile(const char* filePath) {
    ifstream file(filePath);
    if (!file.is_open()) {
        cerr << "Failed to open file: " << filePath << endl;
        return "";
    }
    stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

// Function to initialize OpenGL settings
void initGL() {
    // Compile and link depth shaders
    string depthVertexShaderSource = readFile("depth.vs.txt");
    string depthFragmentShaderSource = readFile("depth.fs.txt");
    GLuint depthVertexShader = compileShader(depthVertexShaderSource.c_str(), GL_VERTEX_SHADER);
    GLuint depthFragmentShader = compileShader(depthFragmentShaderSource.c_str(), GL_FRAGMENT_SHADER);
    depthShaderProgram = linkProgram(depthVertexShader, depthFragmentShader);

    // Compile and link scene shaders
    string sceneVertexShaderSource = readFile("scene.vs.txt");
    string sceneFragmentShaderSource = readFile("scene.fs.txt");
    GLuint sceneVertexShader = compileShader(sceneVertexShaderSource.c_str(), GL_VERTEX_SHADER);
    GLuint sceneFragmentShader = compileShader(sceneFragmentShaderSource.c_str(), GL_FRAGMENT_SHADER);
    sceneShaderProgram = linkProgram(sceneVertexShader, sceneFragmentShader);

#ifdef ANTIALIASING
    // Compile and link FXAA shaders
    string fxaaVertexShaderSource = readFile("fxaa.vs.txt");
    string fxaaFragmentShaderSource = readFile("fxaa.fs.txt");
    GLuint fxaaVertexShader = compileShader(fxaaVertexShaderSource.c_str(), GL_VERTEX_SHADER);
    GLuint fxaaFragmentShader = compileShader(fxaaFragmentShaderSource.c_str(), GL_FRAGMENT_SHADER);
    fxaaShaderProgram = linkProgram(fxaaVertexShader, fxaaFragmentShader);
#endif

    // Get uniform locations for scene shader
    glUseProgram(sceneShaderProgram);
    modelLoc = glGetUniformLocation(sceneShaderProgram, "model");
    viewLoc = glGetUniformLocation(sceneShaderProgram, "view");
    projectionLoc = glGetUniformLocation(sceneShaderProgram, "projection");
    lightPosLoc = glGetUniformLocation(sceneShaderProgram, "lightPos");
    viewPosLoc = glGetUniformLocation(sceneShaderProgram, "viewPos");
    lightSpaceMatrixLoc = glGetUniformLocation(sceneShaderProgram, "lightSpaceMatrix");
    yScaleLoc = glGetUniformLocation(sceneShaderProgram, "yScale");
    glGetUniformLocation(sceneShaderProgram, "cubeColor");

    // Get uniform locations for depth shader
    glUseProgram(depthShaderProgram);
    GLint lightSpaceMatrixLocDepth = glGetUniformLocation(depthShaderProgram, "lightSpaceMatrix");
    GLint modelLocDepth = glGetUniformLocation(depthShaderProgram, "model");

    // Create framebuffer object for shadow mapping
    glGenFramebuffers(1, &depthMapFBO);
    glGenTextures(1, &depthMap);
    glBindTexture(GL_TEXTURE_2D, depthMap);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
    GLfloat borderColor[] = { 1.0, 1.0, 1.0, 1.0 };
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);

    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthMap, 0);
    glDrawBuffer(GL_NONE);
    glReadBuffer(GL_NONE);
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        cerr << "Framebuffer not complete!" << endl;
    }
    glBindFramebuffer(GL_FRAMEBUFFER, 0);

#ifdef ANTIALIASING
    // Create framebuffer for FXAA
    glGenFramebuffers(1, &fxaaFBO);
    glBindFramebuffer(GL_FRAMEBUFFER, fxaaFBO);

    glGenTextures(1, &texColorBuffer);
    glBindTexture(GL_TEXTURE_2D, texColorBuffer);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, PIXEL_WIDTH, PIXEL_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texColorBuffer, 0);

    GLuint rbo;
    glGenRenderbuffers(1, &rbo);
    glBindRenderbuffer(GL_RENDERBUFFER, rbo);
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, PIXEL_WIDTH, PIXEL_HEIGHT);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);

    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        cerr << "FXAA Framebuffer not complete!" << endl;
    }
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
#endif

    // Clean up shaders
    glDeleteShader(depthVertexShader);
    glDeleteShader(depthFragmentShader);
    glDeleteShader(sceneVertexShader);
    glDeleteShader(sceneFragmentShader);
#ifdef ANTIALIASING
    glDeleteShader(fxaaVertexShader);
    glDeleteShader(fxaaFragmentShader);
#endif

    // Initialize VBO and VAO
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);

    glBindVertexArray(VAO);

    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    // Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    // Normal attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
}

// Function to update shader uniforms
void updateSceneUniforms() {
    glm::mat4 model = glm::mat4(1.0f);
    glm::mat4 view = glm::lookAt(
        glm::vec3(camX, camY, camZ),
        glm::vec3(camX + cos(camPitch) * sin(camYaw),
            camY + sin(camPitch),
            camZ + cos(camPitch) * cos(camYaw)),
        glm::vec3(0.0f, 1.0f, 0.0f)
    );
    glm::mat4 projection = glm::perspective(glm::radians(45.0f), (float)PIXEL_WIDTH / (float)PIXEL_HEIGHT, 0.1f, 1000.0f);
    glm::mat4 lightSpaceMatrix = glm::mat4(1.0f); // Placeholder, should be calculated based on light's view/projection matrices

    glUseProgram(sceneShaderProgram);
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
    glUniformMatrix4fv(projectionLoc, 1, GL_FALSE, glm::value_ptr(projection));
    glUniform3fv(lightPosLoc, 1, glm::value_ptr(lightPos));
    glUniform3fv(viewPosLoc, 1, glm::value_ptr(glm::vec3(camX, camY, camZ)));
    glUniformMatrix4fv(lightSpaceMatrixLoc, 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));

    /*
    // Debug output
    cout << "Model matrix: " << glm::to_string(model) << endl;
    cout << "View matrix: " << glm::to_string(view) << endl;
    cout << "Projection matrix: " << glm::to_string(projection) << endl;
    cout << "Light position: " << glm::to_string(lightPos) << endl;
    cout << "View position: " << glm::to_string(glm::vec3(camX, camY, camZ)) << endl;
    */
}

void updateDepthUniforms() {
    glm::mat4 lightSpaceMatrix = glm::mat4(1.0f); // Placeholder, should be calculated based on light's view/projection matrices
    glm::mat4 model = glm::mat4(1.0f);

    glUseProgram(depthShaderProgram);
    GLint lightSpaceMatrixLocDepth = glGetUniformLocation(depthShaderProgram, "lightSpaceMatrix");
    GLint modelLocDepth = glGetUniformLocation(depthShaderProgram, "model");

    glUniformMatrix4fv(lightSpaceMatrixLocDepth, 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));
    glUniformMatrix4fv(modelLocDepth, 1, GL_FALSE, glm::value_ptr(model));
}

// Function to draw a cube
void drawCube(float x, float y, float z, float size, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    if (r + g + b == 0) {
        return;
    }

    float half_size = size / 2;

    // Calculate brightness as the average of the RGB values
    float brightness = (r + g + b) / 765.0f;

    // Use brightness to scale the y-axis size
    float yScale = 1.0f + brightness * 50.0f;

    glm::mat4 model = glm::mat4(1.0f);
    model = glm::translate(model, glm::vec3(x, y, z));
    model = glm::scale(model, glm::vec3(half_size, half_size, half_size));

    // Convert RGB values to [0,1] range
    glm::vec3 color = glm::vec3(r / 255.0f, g / 255.0f, b / 255.0f);

    glUseProgram(sceneShaderProgram);
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glUniform1f(yScaleLoc, yScale);
    glUniform3fv(glGetUniformLocation(sceneShaderProgram, "cubeColor"), 1, glm::value_ptr(color)); // Pass the color

    glBindVertexArray(VAO); // Bind the VAO
    glDrawArrays(GL_TRIANGLES, 0, 36); // Draw the cube
    glBindVertexArray(0); // Unbind the VAO
}

void renderQuad() {
    static unsigned int quadVAO = 0;
    static unsigned int quadVBO;
    if (quadVAO == 0) {
        float quadVertices[] = {
            // positions     // texCoords
            -1.0f,  1.0f,  0.0f, 1.0f,
            -1.0f, -1.0f,  0.0f, 0.0f,
             1.0f, -1.0f,  1.0f, 0.0f,

            -1.0f,  1.0f,  0.0f, 1.0f,
             1.0f, -1.0f,  1.0f, 0.0f,
             1.0f,  1.0f,  1.0f, 1.0f
        };

        glGenVertexArrays(1, &quadVAO);
        glGenBuffers(1, &quadVBO);
        glBindVertexArray(quadVAO);
        glBindBuffer(GL_ARRAY_BUFFER, quadVBO);
        glBufferData(GL_ARRAY_BUFFER, sizeof(quadVertices), &quadVertices, GL_STATIC_DRAW);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));
    }
    glBindVertexArray(quadVAO);
    glDrawArrays(GL_TRIANGLES, 0, 6);
    glBindVertexArray(0);
}

// Function to render the scene
void renderScene(GLuint shaderProgram) {
#ifdef ANTIALIASING
    // If rendering the scene, bind the FXAA framebuffer first
    if (shaderProgram == sceneShaderProgram) {
        glBindFramebuffer(GL_FRAMEBUFFER, fxaaFBO);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    }
#endif

    glUseProgram(shaderProgram);

    if (shaderProgram == sceneShaderProgram) {
        updateSceneUniforms();
    }
    else if (shaderProgram == depthShaderProgram) {
        updateDepthUniforms();
    }

    std::lock_guard<std::mutex> guard(pixelsMutex);

    float cubeSize = 1.0f; // Adjust cube size for better visibility
    for (int z = 0; z < PIXEL_HEIGHT / 10; ++z) {
        for (int x = 0; x < PIXEL_WIDTH / 10; ++x) {
            int index = z * (PIXEL_WIDTH / 10) + x;
            uint32_t color = pixels[index];
            uint8_t a = (color >> 24) & 0xFF;
            uint8_t r = (color >> 16) & 0xFF;
            uint8_t g = (color >> 8) & 0xFF;
            uint8_t b = color & 0xFF;
            /*
            if (index == currentIndex) {
                lightPos[0] = (9*lightPos[0] + x * cubeSize - ((PIXEL_WIDTH / 10) * cubeSize / 2) + cubeSize / 2) / 10;
                lightPos[1] = (6*lightPos[1] + (((PIXEL_HEIGHT / 2) - 1) - z) * cubeSize - ((PIXEL_HEIGHT / 2) * cubeSize / 2))/ 10;
            }
            */
            drawCube(x * 0.5f - (118.4f * 0.5f / 2) + 0.5f / 2,
                0.0f,
                (((666.0f / 2) - 1) - z) * 0.5f - ((666.f/ 2) * 0.5f / 2),
                cubeSize, r, g, b, a);
        }
    }

    // drawCube(lightPos[0], lightPos[1], lightPos[2], cubeSize, 64, 64, 64, 255);

#ifdef ANTIALIASING
    // If rendering the scene, apply FXAA
    if (shaderProgram == sceneShaderProgram) {
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glUseProgram(fxaaShaderProgram);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, texColorBuffer);
        glUniform1i(glGetUniformLocation(fxaaShaderProgram, "screenTexture"), 0);
        glUniform2f(glGetUniformLocation(fxaaShaderProgram, "inverseScreenSize"), 1.0f / PIXEL_WIDTH, 1.0f / PIXEL_HEIGHT);

        // Render a full-screen quad
        renderQuad();
    }
#endif
}

void updateLightPosition() {
    return;
    lightPos[0] = lightDistance * cos(lightAngle);
    lightPos[2] = lightDistance * sin(lightAngle) + 50.0f;

    cout << "light: " << lightAngle << ", x: " << lightPos[0] << ", z: " << lightPos[2] << ", theta: " << lightAngle << endl;

    lightAngle += lightSpeed;
    if (lightAngle > 6.283185307179586) {
        lightAngle -= 6.283185307179586;
    } else if (lightAngle < 0) {
        lightAngle += 6.283185307179586;
    }
}

// Main graphics rendering thread
int graphicsThread(int argc, char* argv[]) {
    // Initialize GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
    }

    // Create a GLFW window
    GLFWwindow* window = glfwCreateWindow(PIXEL_WIDTH, PIXEL_HEIGHT, "Pixels", NULL, NULL);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }

    // Make the OpenGL context current
    glfwMakeContextCurrent(window);

    // Set the framebuffer size callback to handle window resizing
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    // Initialize GLEW
    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW" << std::endl;
        return -1;
    }

    // Initialize OpenGL settings and shaders
    initGL();

    // Enable depth testing for 3D rendering
    glEnable(GL_DEPTH_TEST);

    // Enable blending for transparency
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    glEnable(GL_DEBUG_OUTPUT);
    glDebugMessageCallback([](GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar* message, const void* userParam) {
        std::cerr << "GL ERROR: " << message << std::endl;
        }, nullptr);

#ifdef MOUSE_INPUT
    glfwSetCursorPosCallback(window, mouseCallback);
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED); // Hide the cursor and capture it
#endif
    // Main rendering loop
    while (!glfwWindowShouldClose(window)) {
        // Poll for and process events
        glfwPollEvents();

#ifdef KEYBOARD_INPUT
        // Process keyboard input for camera movement
        processInput(window);
#endif
        updateLightPosition();

        // Clear the color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // 1. Render depth map from light's perspective
        glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT);
        glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
        glClear(GL_DEPTH_BUFFER_BIT);
        renderScene(depthShaderProgram);
        glBindFramebuffer(GL_FRAMEBUFFER, 0);

        // 2. Render scene with shadows
        glViewport(0, 0, PIXEL_WIDTH, PIXEL_HEIGHT);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        renderScene(sceneShaderProgram);

        // Swap front and back buffers
        glfwSwapBuffers(window);

        // Wait for the specified frame delay
        glfwWaitEventsTimeout(FRAME_DELAY / 1000.0);
    }

    // Clean up and terminate GLFW
    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}

// Main function
int main(int argc, char* argv[]) {
    // Create a thread for the graphics rendering
    thread gThread(graphicsThread, argc, argv);

#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif

    cout << "initializing server socket" << endl;
    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == INVALID_SOCKET) {
        cerr << "Can't create a socket!";
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
    int clientSize = sizeof(client);

    while (true) {
        cout << "ready to accept clients" << endl;
        SOCKET clientSocket = accept(serverSocket, (sockaddr*)&client, &clientSize);
        cout << "accepted client connection" << endl;
        thread clientThread(handleClient, clientSocket);
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
