#pragma once
#include <algorithm>            // For sort funcionality
#include <iostream>             // For standard input/output operations
#include <bitset>               // For manipulating bits and performing bitwise operations
#include <fstream>              // For file input/output operations
#include <sstream>              // For string stream operations
#include <thread>               // For multithreading support
#include <mutex>                // For mutual exclusion to prevent race conditions
#include <vector>               // For using the vector container from the standard library
#include <cstring>              // For manipulating C-style strings
#include <cstdlib>              // For general utilities including dynamic memory management
#include <glew.h>               // For managing OpenGL extensions
#include <glfw3.h>              // For creating windows with OpenGL contexts and handling input/events
#include <glm.hpp>              // For using OpenGL Mathematics library
#define GLM_ENABLE_EXPERIMENTAL // For enabling experimental features in GLM
#include <gtc/matrix_transform.hpp> // For transformations such as translation, rotation, and scaling
#include <gtc/type_ptr.hpp>     // For converting GLM types to pointers
#include <gtx/string_cast.hpp>  // For converting GLM types to strings

#include "block.h"
#include "shaderProgram.h"
#include "camera.h"
#include "colorHandler.h"
#include "clientHandler.h"

using namespace std;

// Constants for window and shadow map dimensions
#define FRAME_DELAY 30
#define FRAME_DELAY_IN_SECONDS (FRAME_DELAY / 1000.0f)
#define PIXEL_WIDTH 1184
#define PIXEL_HEIGHT 666
#define PIXEL_COUNT ((PIXEL_WIDTH/10) * (PIXEL_HEIGHT/10))
#define PIXEL_ASPECT_RATIO 1.777777777777778f
#define HORIZ_BARS 66
#define VERT_BARS 66
#define HALF_HORIZ_BARS (HORIZ_BARS / 2)
#define HALF_VERT_BARS (VERT_BARS / 2)
#define BARS_COUNT (HORIZ_BARS * VERT_BARS)
#define SHADOW_WIDTH 666
#define SHADOW_HEIGHT 666

// #define KEYBOARD_INPUT
// #define KEYBOARD_CONTROLS_CAMERA
// #define KEYBOARD_CONTROLS_LIGHT
// #define MOUSE_INPUT
#define ANTIALIASING
#define MSAA
// #define RAYTRACING
#define DEBUG

vector<Block*>* blocks = new vector<Block*>();

size_t currentIndex = 0;
mutex pixelsMutex;

// Constants for movement speed and mouse sensitivity
const float speed = 0.25f;
const float sensitivity = 0.0005f;

float lightAngle = 0;
float lightDistance = 20.0f;
float lightSpeed = 0.0174533f;

// Light position
glm::vec3 lightPos(-40.0f, 300.0f, 100.0f);
//glm::vec3 lightPos(0.0f, 50.0f, 0.0f);

// Shader and framebuffer objects
GLuint depthMapFBO, depthMap;
#ifdef ANTIALIASING
ShaderProgram* fxaaShaderProgram;
GLuint fxaaFBO, texColorBuffer;
#ifdef MSAA
GLuint msaaColorBuffer, msaaFBO, msaaRBO;
#endif
#endif
ShaderProgram* depthShaderProgram;
ShaderProgram* sceneShaderProgram;

#ifdef RAYTRACING
GLuint rayTracingShaderProgram;
GLuint ssboSpheres;
GLuint ssboResult;
GLuint resultTexture;
#endif

// Uniform locations for shaders
GLint modelLoc, viewLoc, projectionLoc, lightPosLoc, viewPosLoc, lightSpaceMatrixLoc, yScaleLoc;

// VBO and VAO
unsigned int VBO, VAO;

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

struct Sphere {
    glm::vec3 center;
    float radius;
    glm::vec3 color;
};

int numSpheres = 1; // Adjust the number of spheres as needed


// Function to link a compute shader into a program
GLuint linkComputeProgram(GLuint computeShader) {
    GLuint program = glCreateProgram();
    glAttachShader(program, computeShader);
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

void checkGLError(const char* stmt, const char* fname, int line) {
    GLenum err = glGetError();
    if (err != GL_NO_ERROR) {
        std::cerr << "OpenGL error " << err << " at " << stmt << " in " << fname << " line " << line << std::endl;
        exit(1);
    }
}

#define GL_CHECK(stmt) do { \
    stmt; \
    checkGLError(#stmt, __FILE__, __LINE__); \
} while (0)

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

        GL_CHECK(glGenVertexArrays(1, &quadVAO));
        GL_CHECK(glGenBuffers(1, &quadVBO));
        GL_CHECK(glBindVertexArray(quadVAO));
        GL_CHECK(glBindBuffer(GL_ARRAY_BUFFER, quadVBO));
        GL_CHECK(glBufferData(GL_ARRAY_BUFFER, sizeof(quadVertices), &quadVertices, GL_STATIC_DRAW));
        GL_CHECK(glEnableVertexAttribArray(0));
        GL_CHECK(glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0));
        GL_CHECK(glEnableVertexAttribArray(1));
        GL_CHECK(glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float))));
    }
    GL_CHECK(glBindVertexArray(quadVAO));
    GL_CHECK(glDrawArrays(GL_TRIANGLES, 0, 6));
    GL_CHECK(glBindVertexArray(0));
}

#ifdef RAYTRACING
void initRayTracing() {
    cout << "initializing ray tracing" << endl;
    // Load and compile the compute shader
    std::string raytracingComputeShaderSource = ShaderProgram::readFile("raytracing.comp");
    GLuint raytracingComputeShader = ShaderProgram::compileShader(raytracingComputeShaderSource.c_str(), GL_COMPUTE_SHADER);
    if (!raytracingComputeShader) {
        std::cerr << "ERROR: Compute shader compilation failed." << std::endl;
        return;
    }

    // Link compute shader program
    rayTracingShaderProgram = linkComputeProgram(raytracingComputeShader);
    if (!rayTracingShaderProgram) {
        std::cerr << "ERROR: Compute shader program linking failed." << std::endl;
        return;
    }

    glDeleteShader(raytracingComputeShader);

    // Initialize SSBO for spheres
    glGenBuffers(1, &ssboSpheres);
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboSpheres);
    glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(Sphere) * numSpheres, NULL, GL_DYNAMIC_DRAW);
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssboSpheres);

    // Initialize SSBO for result
    glGenBuffers(1, &ssboResult);
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboResult);
    glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(glm::vec4) * PIXEL_WIDTH * PIXEL_HEIGHT, NULL, GL_DYNAMIC_DRAW);
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, ssboResult);

    // Initialize result texture
    glGenTextures(1, &resultTexture);
    glBindTexture(GL_TEXTURE_2D, resultTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, PIXEL_WIDTH, PIXEL_HEIGHT, 0, GL_RGBA, GL_FLOAT, NULL);
    glBindTexture(GL_TEXTURE_2D, 0);
}

void renderRayTracedScene() {
    cout << "rendering ray traced scene" << endl;
    if (rayTracingShaderProgram == 0) {
        std::cerr << "ERROR: rayTracingShaderProgram is not valid." << std::endl;
        return;
    }

    // Use the compute shader program
    glUseProgram(rayTracingShaderProgram);

    // Update SSBOs with sphere data
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboSpheres);
    Sphere spheres[] = {
        { glm::vec3(0.0f, 0.0f, -5.0f), 1.0f, glm::vec3(1.0f, 0.0f, 0.0f) }
        // Add more spheres here
    };
    glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, sizeof(spheres), spheres);

    // Check for any OpenGL errors
    GLenum err;
    while ((err = glGetError()) != GL_NO_ERROR) {
        std::cerr << "OpenGL error after updating SSBOs: " << err << std::endl;
    }

    // Set uniforms
    GLint cameraPosLoc = glGetUniformLocation(rayTracingShaderProgram, "cameraPos");
    GLint resolutionLoc = glGetUniformLocation(rayTracingShaderProgram, "resolution");

    if (cameraPosLoc == -1 || resolutionLoc == -1) {
        std::cerr << "ERROR: Failed to get uniform locations." << std::endl;
        return;
    }

    glUniform3fv(cameraPosLoc, 1, glm::value_ptr(glm::vec3(camX, camY, camZ)));
    glUniform2f(resolutionLoc, PIXEL_WIDTH, PIXEL_HEIGHT);

    // Dispatch compute shader
    glDispatchCompute((GLuint)(PIXEL_WIDTH + 15) / 16, (GLuint)(PIXEL_HEIGHT + 15) / 16, 1);

    // Ensure compute shader has completed
    glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT | GL_TEXTURE_FETCH_BARRIER_BIT);

    // Check for any OpenGL errors
    while ((err = glGetError()) != GL_NO_ERROR) {
        std::cerr << "OpenGL error after dispatching compute shader: " << err << std::endl;
    }

    // Copy SSBO result to texture
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboResult);
    glBindTexture(GL_TEXTURE_2D, resultTexture);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, PIXEL_WIDTH, PIXEL_HEIGHT, GL_RGBA, GL_FLOAT, NULL);

    // Render the result texture
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glBindTexture(GL_TEXTURE_2D, resultTexture);
    renderQuad();
    glBindTexture(GL_TEXTURE_2D, 0);
}

void cleanup(GLFWwindow* window) {
    glDeleteProgram(rayTracingShaderProgram);
    glDeleteBuffers(1, &ssboSpheres);
    glDeleteBuffers(1, &ssboResult);
    glDeleteTextures(1, &resultTexture);
    glfwDestroyWindow(window);
    glfwTerminate();
}
#endif 

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

// Function to initialize OpenGL settings
void initGL() {
    depthShaderProgram = new ShaderProgram("depth.vs.txt", "depth.fs.txt");
    sceneShaderProgram = new ShaderProgram("scene.vs.txt", "scene.fs.txt");

#ifdef ANTIALIASING
    // If ANTIALIASING is defined, compile and link FXAA shaders
    // FXAA (Fast Approximate Anti-Aliasing) is a post-processing technique to smooth jagged edges
    fxaaShaderProgram = new ShaderProgram("fxaa.vs.txt", "fxaa.fs.txt");
#endif

    // Get uniform locations for scene shader
    // Use the scene shader program
    glUseProgram(sceneShaderProgram->program);
    // Retrieve uniform locations for transformation matrices and lighting parameters
    // These locations are used to set the values of the corresponding uniforms in the shader
    modelLoc = glGetUniformLocation(sceneShaderProgram->program, "model");
    viewLoc = glGetUniformLocation(sceneShaderProgram->program, "view");
    projectionLoc = glGetUniformLocation(sceneShaderProgram->program, "projection");
    lightPosLoc = glGetUniformLocation(sceneShaderProgram->program, "lightPos");
    viewPosLoc = glGetUniformLocation(sceneShaderProgram->program, "viewPos");
    lightSpaceMatrixLoc = glGetUniformLocation(sceneShaderProgram->program, "lightSpaceMatrix");
    yScaleLoc = glGetUniformLocation(sceneShaderProgram->program, "yScale");
    glGetUniformLocation(sceneShaderProgram->program, "cubeColor");

    // Get uniform locations for depth shader
    // Use the depth shader program
    glUseProgram(depthShaderProgram->program);
    // Retrieve uniform locations for transformation matrices specific to the depth shader
    GLint lightSpaceMatrixLocDepth = glGetUniformLocation(depthShaderProgram->program, "lightSpaceMatrix");
    GLint modelLocDepth = glGetUniformLocation(depthShaderProgram->program, "model");

    // Create framebuffer object for shadow mapping
    // A framebuffer is an OpenGL object that contains buffers for color, depth, and stencil data
    glGenFramebuffers(1, &depthMapFBO);  // Generate one framebuffer object
    // Create a texture to store the depth map
    glGenTextures(1, &depthMap);  // Generate one texture object
    glBindTexture(GL_TEXTURE_2D, depthMap);  // Bind the texture as a 2D texture
    // Allocate storage for the depth map texture
    // SHADOW_WIDTH and SHADOW_HEIGHT define the resolution of the shadow map
    // GL_DEPTH_COMPONENT specifies that the texture will store depth values
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, NULL);
    // Set texture parameters for the depth map
    // GL_NEAREST specifies nearest-neighbor filtering (no interpolation)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    // GL_CLAMP_TO_BORDER clamps the texture coordinates to the edge of the texture
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
    // Define border color for the depth map texture
    // The border color is used when texture coordinates are outside the [0, 1] range
    GLfloat borderColor[] = { 1.0, 1.0, 1.0, 1.0 };
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);

    // Attach the depth map texture to the framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);  // Bind the framebuffer
    // Attach the depth map texture as the depth attachment of the framebuffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthMap, 0);
    // Disable color buffer drawing and reading
    // GL_NONE disables both drawing to and reading from the color buffer
    glDrawBuffer(GL_NONE);
    glReadBuffer(GL_NONE);
    // Check if the framebuffer is complete
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        cerr << "Framebuffer not complete!" << endl;  // Print an error message if the framebuffer is not complete
    }
    // Unbind the framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0);

#ifdef ANTIALIASING
#ifdef MSAA
    // If both ANTIALIASING and MSAA are defined, create a multisample framebuffer for scene rendering
    // MSAA (Multisample Anti-Aliasing) is a technique to reduce aliasing by sampling multiple times per pixel
    glGenFramebuffers(1, &msaaFBO);  // Generate one framebuffer object
    glBindFramebuffer(GL_FRAMEBUFFER, msaaFBO);  // Bind the framebuffer

    // Create a multisample texture for color attachment
    glGenTextures(1, &msaaColorBuffer);  // Generate one texture object
    glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, msaaColorBuffer);  // Bind the texture as a multisample 2D texture
    // Allocate storage for the multisample texture
    // GL_TEXTURE_2D_MULTISAMPLE specifies a multisample 2D texture
    // 8 specifies the number of samples per pixel
    // GL_RGB specifies the texture format
    // PIXEL_WIDTH and PIXEL_HEIGHT define the resolution of the texture
    glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, 8, GL_RGB, PIXEL_WIDTH, PIXEL_HEIGHT, GL_TRUE);
    // Attach the multisample texture as the color attachment of the framebuffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, msaaColorBuffer, 0);

    // Create a renderbuffer object for depth and stencil attachment
    glGenRenderbuffers(1, &msaaRBO);  // Generate one renderbuffer object
    glBindRenderbuffer(GL_RENDERBUFFER, msaaRBO);  // Bind the renderbuffer
    // Allocate storage for the renderbuffer
    // GL_RENDERBUFFER specifies a renderbuffer object
    // GL_DEPTH24_STENCIL8 specifies a combined depth and stencil buffer with 24-bit depth and 8-bit stencil
    glRenderbufferStorageMultisample(GL_RENDERBUFFER, 8, GL_DEPTH24_STENCIL8, PIXEL_WIDTH, PIXEL_HEIGHT);
    // Attach the renderbuffer as the depth and stencil attachment of the framebuffer
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, msaaRBO);

    // Check if the multisample framebuffer is complete
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        cerr << "MSAA Framebuffer not complete!" << endl;  // Print an error message if the framebuffer is not complete
    }
    // Unbind the framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
#endif
    // Create a framebuffer for FXAA
    glGenFramebuffers(1, &fxaaFBO);  // Generate one framebuffer object
    glBindFramebuffer(GL_FRAMEBUFFER, fxaaFBO);  // Bind the framebuffer

    // Create a texture for color attachment
    glGenTextures(1, &texColorBuffer);  // Generate one texture object
    glBindTexture(GL_TEXTURE_2D, texColorBuffer);  // Bind the texture as a 2D texture
    // Allocate storage for the texture
    // GL_RGB specifies the texture format
    // PIXEL_WIDTH and PIXEL_HEIGHT define the resolution of the texture
    // GL_UNSIGNED_BYTE specifies the data type of the texture data
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, PIXEL_WIDTH, PIXEL_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
    // Set texture parameters for the texture
    // GL_LINEAR specifies linear filtering (interpolation)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    // Attach the texture as the color attachment of the framebuffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texColorBuffer, 0);

    // Create a renderbuffer object for depth and stencil attachment
    GLuint rbo;  // Renderbuffer object
    glGenRenderbuffers(1, &rbo);  // Generate one renderbuffer object
    glBindRenderbuffer(GL_RENDERBUFFER, rbo);  // Bind the renderbuffer
    // Allocate storage for the renderbuffer
    // GL_DEPTH24_STENCIL8 specifies a combined depth and stencil buffer with 24-bit depth and 8-bit stencil
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, PIXEL_WIDTH, PIXEL_HEIGHT);
    // Attach the renderbuffer as the depth and stencil attachment of the framebuffer
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);

    // Check if the FXAA framebuffer is complete
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        cerr << "FXAA Framebuffer not complete!" << endl;  // Print an error message if the framebuffer is not complete
    }
    // Unbind the framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
#endif

    // Clean up shaders by deleting them after linking
    // Shaders are no longer needed once they are linked into a program
    depthShaderProgram->deleteShaders();
    sceneShaderProgram->deleteShaders();
#ifdef ANTIALIASING
    fxaaShaderProgram->deleteShaders();
#endif

    // Initialize Vertex Buffer Object (VBO) and Vertex Array Object (VAO)
    // VBO stores vertex data in GPU memory
    // VAO stores the configuration of vertex attributes
    glGenVertexArrays(1, &VAO);  // Generate one VAO
    glGenBuffers(1, &VBO);  // Generate one VBO

    // Bind VAO
    glBindVertexArray(VAO);

    // Bind VBO and transfer vertex data to buffer
    glBindBuffer(GL_ARRAY_BUFFER, VBO);  // Bind the VBO as the current array buffer
    // Transfer vertex data to the VBO
    // sizeof(vertices) specifies the size of the data in bytes
    // vertices is the array of vertex data
    // GL_STATIC_DRAW indicates that the data will be modified once and used many times
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    // Specify layout of vertex data: position attribute
    // glVertexAttribPointer defines how vertex attributes are stored in the VBO
    // 0 specifies the index of the vertex attribute (position)
    // 3 specifies the number of components (x, y, z)
    // GL_FLOAT specifies the data type
    // GL_FALSE specifies that the data should not be normalized
    // 6 * sizeof(float) specifies the stride (distance between consecutive vertex attributes)
    // (void*)0 specifies the offset of the first component
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);  // Enable the vertex attribute

    // Specify layout of vertex data: normal attribute
    // 1 specifies the index of the vertex attribute (normal)
    // 3 specifies the number of components (x, y, z)
    // GL_FLOAT specifies the data type
    // GL_FALSE specifies that the data should not be normalized
    // 6 * sizeof(float) specifies the stride (distance between consecutive vertex attributes)
    // (void*)(3 * sizeof(float)) specifies the offset of the first component
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);  // Enable the vertex attribute

    // Unbind VBO and VAO
    glBindBuffer(GL_ARRAY_BUFFER, 0);  // Unbind the VBO
    glBindVertexArray(0);  // Unbind the VAO

#ifdef RAYTRACING
    initRayTracing();
#endif
}

// Function to update shader uniforms
void updateSceneUniforms(Camera* camera) {
    float cosCamPitch = cos(camera->xRotation);

    glm::mat4 model = glm::mat4(1.0f);
    glm::mat4 view = glm::lookAt(
        glm::vec3(camera->xPosition, camera->yPosition, camera->zPosition),
        glm::vec3(camera->xPosition + cosCamPitch * sin(camera->yRotation),
            camera->yPosition + sin(camera->xRotation),
            camera->zPosition + cosCamPitch * cos(camera->yRotation)),
        glm::vec3(0.0f, 1.0f, 0.0f)
    );
    glm::mat4 projection = glm::perspective(0.785398f, PIXEL_ASPECT_RATIO, 0.1f, 1000.0f);
    glm::mat4 lightSpaceMatrix = glm::mat4(1.0f); // Placeholder, should be calculated based on light's view/projection matrices

    glUseProgram(sceneShaderProgram->program);
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
    glUniformMatrix4fv(projectionLoc, 1, GL_FALSE, glm::value_ptr(projection));
    glUniform3fv(lightPosLoc, 1, glm::value_ptr(lightPos));
    glUniform3fv(viewPosLoc, 1, glm::value_ptr(glm::vec3(camera->xPosition, camera->yPosition, camera->zPosition)));
    glUniformMatrix4fv(lightSpaceMatrixLoc, 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));
}

void updateDepthUniforms() {
    glm::mat4 lightSpaceMatrix = glm::mat4(1.0f); // Placeholder, should be calculated based on light's view/projection matrices
    glm::mat4 model = glm::mat4(1.0f);

    glUseProgram(depthShaderProgram->program);
    GLint lightSpaceMatrixLocDepth = glGetUniformLocation(depthShaderProgram->program, "lightSpaceMatrix");
    GLint modelLocDepth = glGetUniformLocation(depthShaderProgram->program, "model");

    glUniformMatrix4fv(lightSpaceMatrixLocDepth, 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));
    glUniformMatrix4fv(modelLocDepth, 1, GL_FALSE, glm::value_ptr(model));
}

// Function to render the scene
// This function is responsible for rendering the entire scene using the specified shader program
void renderScene(ShaderProgram* shaderProgram, Camera* camera) {
#ifdef ANTIALIASING
#ifdef MSAA
    // If both ANTIALIASING and MSAA are defined and the scene shader program is used
    // Bind the MSAA framebuffer to start rendering with multisample anti-aliasing
    if (shaderProgram == sceneShaderProgram) {
        glBindFramebuffer(GL_FRAMEBUFFER, msaaFBO);  // Bind the MSAA framebuffer
        // Clear the color and depth buffers to prepare for new frame rendering
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    }
#endif
#endif

    // Use the specified shader program for rendering
    glUseProgram(shaderProgram->program);

    // Update uniforms based on the shader program being used
    if (shaderProgram == sceneShaderProgram) {
        // If the scene shader program is used, update the scene-related uniforms
        updateSceneUniforms(camera);
    }
    else if (shaderProgram == depthShaderProgram) {
        // If the depth shader program is used, update the depth-related uniforms
        updateDepthUniforms();
    }

    // Lock the mutex to safely access the pixel data

    {
        std::lock_guard<std::mutex> guard(pixelsMutex);

        auto block_iterator = blocks->begin();
        uint32_t color = 0;
        int pixelIndex = 0;
        glm::vec3 camPositionVec3 = glm::vec3(camera->xPosition, camera->yPosition, camera->zPosition);
        for (int z = 0; z < VERT_BARS; ++z) {
            float zCoord = z * Block::size - (float)(HALF_VERT_BARS);
            for (int x = 0; x < HORIZ_BARS; ++x, ++block_iterator) {
                pixelIndex = z * HORIZ_BARS + x;

                (*block_iterator)->x = x * Block::size - (float)HALF_HORIZ_BARS;
                // block->y = 0.0f;
                (*block_iterator)->z = zCoord;

                (*block_iterator)->distance = glm::length(camPositionVec3 - glm::vec3((*block_iterator)->x, (*block_iterator)->y, (*block_iterator)->z));
                // cubes->push_back(std::make_tuple(distance, x * Block::size - (float)HALF_HORIZ_BARS, zCoord, glm::vec4(r / 255.0f, g / 255.0f, b / 255.0f, a / 255.0f)));
            }
        }
        /*
        sort(blocks->begin(), blocks->end(), [](Block* a, Block* b) {
            return a->distance > b->distance;  // Sort by distance in descending order
            });
        */
        for (int i = 0; i < blocks->size(); i++) {
            blocks->at(i)->draw(sceneShaderProgram, &modelLoc, &yScaleLoc, &VAO);
        }
        
    }
    /*
    block_iterator = blocks->begin();
    while (block_iterator != blocks->end()) {
        block = *block_iterator;
        block->draw(sceneShaderProgram, &modelLoc, &yScaleLoc, &VAO);
        block_iterator++;
    }
    */

#ifdef ANTIALIASING
    // Resolve multisampled framebuffer to a regular framebuffer if antialiasing is enabled
    if (shaderProgram == sceneShaderProgram) {
#ifdef MSAA
        // Bind the MSAA framebuffer for reading
        glBindFramebuffer(GL_READ_FRAMEBUFFER, msaaFBO);
#endif
        // Bind the FXAA framebuffer for drawing
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, fxaaFBO);
        // Blit (copy) the multisampled framebuffer to the regular framebuffer
        // This resolves the multisampled image to a single-sample image
        glBlitFramebuffer(0, 0, PIXEL_WIDTH, PIXEL_HEIGHT, 0, 0, PIXEL_WIDTH, PIXEL_HEIGHT, GL_COLOR_BUFFER_BIT, GL_NEAREST);
        // Unbind the framebuffer to render to the default framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        // Clear the color and depth buffers to prepare for new frame rendering
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Apply FXAA (Fast Approximate Anti-Aliasing)
        glUseProgram(fxaaShaderProgram->program);  // Use the FXAA shader program
        glActiveTexture(GL_TEXTURE0);  // Activate texture unit 0
        glBindTexture(GL_TEXTURE_2D, texColorBuffer);  // Bind the texture containing the resolved image
        // Set the screen texture uniform in the FXAA shader
        glUniform1i(glGetUniformLocation(fxaaShaderProgram->program, "screenTexture"), 0);
        // Set the inverse screen size uniform in the FXAA shader
        glUniform2f(glGetUniformLocation(fxaaShaderProgram->program, "inverseScreenSize"), 1.0f / PIXEL_WIDTH, 1.0f / PIXEL_HEIGHT);

        // Render a full-screen quad to apply FXAA to the entire image
        renderQuad();
    }
#endif
}
void updateLightPosition() {
    return;
    lightPos[0] = lightDistance * cos(lightAngle);
    lightPos[2] = lightDistance * sin(lightAngle) + 50.0f;

    lightAngle += lightSpeed;
    if (lightAngle > 6.283185307179586F) {
        lightAngle -= 6.283185307179586F;
    }
    else if (lightAngle < 0) {
        lightAngle += 6.283185307179586F;
    }
}

// Main graphics rendering thread
int graphicsThread(int argc, char* argv[]) {
    Camera* camera = new Camera();
    // Initialize GLFW
    // GLFW is a library that creates windows with OpenGL contexts and manages input/events
    if (!glfwInit()) {  // Initialize the GLFW library
        std::cerr << "Failed to initialize GLFW" << std::endl;  // Print an error message if initialization fails
        return -1;  // Return an error code if GLFW initialization fails
    }

#ifdef ANTIALIASING
#ifdef MSAA
    // If both ANTIALIASING and MSAA are defined, request 8x MSAA (Multisample Anti-Aliasing)
    glfwWindowHint(GLFW_SAMPLES, 8);  // Set the number of samples per pixel to 8 for MSAA
#endif
#ifndef MSAA
    // If ANTIALIASING is defined but not MSAA, request 4x FXAA (Fast Approximate Anti-Aliasing)
    glfwWindowHint(GLFW_SAMPLES, 4);  // Set the number of samples per pixel to 4 for FXAA
#endif
#endif

    // Create a GLFW window
    // PIXEL_WIDTH and PIXEL_HEIGHT define the dimensions of the window
    // "Pixels" is the title of the window
    // The last two NULL arguments specify default monitor and no shared context
    GLFWwindow* window = glfwCreateWindow(PIXEL_WIDTH, PIXEL_HEIGHT, "Pixels", NULL, NULL);
    if (!window) {  // Check if the window was created successfully
        std::cerr << "Failed to create GLFW window" << std::endl;  // Print an error message if window creation fails
        glfwTerminate();  // Terminate GLFW to clean up resources
        return -1;  // Return an error code if window creation fails
    }

    // Make the OpenGL context current
    // This binds the OpenGL context to the current thread
    glfwMakeContextCurrent(window);

    // Set the framebuffer size callback to handle window resizing
    // This callback is called whenever the window is resized
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    // Initialize GLEW
    // GLEW is a library that manages OpenGL extensions, making it easier to use advanced features
    if (glewInit() != GLEW_OK) {  // Initialize the GLEW library
        std::cerr << "Failed to initialize GLEW" << std::endl;  // Print an error message if initialization fails
        return -1;  // Return an error code if GLEW initialization fails
    }

    // Initialize OpenGL settings and shaders
    // This function sets up shaders, framebuffers, and other OpenGL settings needed for rendering
    initGL();

    // Enable depth testing for 3D rendering
    // Depth testing ensures that pixels closer to the camera are rendered in front of those further away
    glEnable(GL_DEPTH_TEST);

    // Enable blending for transparency
    // Blending allows for transparent rendering by combining the color of an object with the background color
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);  // Set the blending function for transparency

#ifdef MSAA
    // If MSAA is defined, enable multisample anti-aliasing
    glEnable(GL_MULTISAMPLE);  // Enable MSAA, which helps smooth out edges in the rendered image
#endif

    // Enable debug output
    // This allows OpenGL to provide detailed error messages and debugging information
    glEnable(GL_DEBUG_OUTPUT);
    // Set the debug message callback function
    // This function will be called whenever an OpenGL error or warning occurs
    glDebugMessageCallback([](GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar* message, const void* userParam) {
        std::cerr << "GL ERROR: " << message << std::endl;  // Print OpenGL error messages to the console
        }, nullptr);

#ifdef MOUSE_INPUT
    // If MOUSE_INPUT is defined, set the cursor position callback and hide the cursor
    // This callback is called whenever the mouse moves
    glfwSetCursorPosCallback(window, mouseCallback);
    // Hide the cursor and capture it within the window
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
#endif

    // Main rendering loop
    // This loop continues until the window should close, processing input and rendering frames
    while (!glfwWindowShouldClose(window)) {
        // Poll for and process events
        // This handles events such as keyboard and mouse input
        glfwPollEvents();

#ifdef KEYBOARD_INPUT
        // If KEYBOARD_INPUT is defined, process keyboard input for camera movement
        processInput(window);  // Function to handle keyboard input
#endif

        // Update the position of the light source in the scene
        // updateLightPosition();

        // Rotate the camera around the center of the scene
        // camera->rotateAroundCenter();

#ifdef RAYTRACING
        renderRayTracedScene();
#else
        // Clear the color and depth buffers
        // This prepares the buffers for the next frame by clearing old data
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // 1. Render depth map from light's perspective
        // Set the viewport to the size of the shadow map
        glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT);
        // Bind the framebuffer for depth map rendering
        glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
        // Clear the depth buffer to prepare for new depth data
        glClear(GL_DEPTH_BUFFER_BIT);
        // Render the scene using the depth shader program
        renderScene(depthShaderProgram, camera);
        // Unbind the framebuffer to return to the default framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0);

        // 2. Render scene with shadows
        // Set the viewport to the size of the window
        glViewport(0, 0, PIXEL_WIDTH, PIXEL_HEIGHT);
        // Clear the color and depth buffers to prepare for rendering the scene
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        // Render the scene using the scene shader program

        renderScene(sceneShaderProgram, camera);
#endif


        // Swap front and back buffers
        // This displays the rendered image on the screen
        glfwSwapBuffers(window);

        // Wait for the specified frame delay
        // This controls the frame rate by pausing for a specified amount of time
        glfwWaitEventsTimeout(FRAME_DELAY_IN_SECONDS);
    }

    // Clean up and terminate GLFW
    // Destroy the window and free associated resources
    glfwDestroyWindow(window);
    // Terminate GLFW and free any remaining resources
    glfwTerminate();

#ifdef RAYTRACING
    cleanup(window);
#endif

    return 0;  // Return success code indicating the program ended without errors
}

// Main function
int main(int argc, char* argv[]) {
    static int numClients = 0;
    for (int i = 0; i < BARS_COUNT; i++) {
        blocks->push_back(new Block());
    }

    // Create a thread for the graphics rendering
    thread gThread(graphicsThread, argc, argv);
    int x = BARS_COUNT;
    ClientHandler<Block>* clientHandler = new ClientHandler<Block>(&pixelsMutex, blocks, x, reinterpret_cast<int*>(&currentIndex), &numClients);
    clientHandler->initialize();

    gThread.join();
    return 0;
}
