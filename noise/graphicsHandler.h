#pragma once
#include <vector>
#include <thread>               // For multithreading support
#include <mutex>                // For mutual exclusion to prevent race conditions
#include <glew.h>               // For managing OpenGL extensions
#include <glfw3.h>              // For creating windows with OpenGL contexts and handling input/events
#include <glm.hpp>              // For using OpenGL Mathematics library
#define GLM_ENABLE_EXPERIMENTAL // For enabling experimental features in GLM
#include <gtc/matrix_transform.hpp> // For transformations such as translation, rotation, and scaling
#include <gtc/type_ptr.hpp>     // For converting GLM types to pointers
#include <gtx/string_cast.hpp>  // For converting GLM types to strings
#include "shaderProgram.h"
#include "camera.h"
#include "block.h"

// Constants for window and shadow map dimensions
#define FRAME_DELAY 30
#define FRAME_DELAY_IN_SECONDS (FRAME_DELAY / 1000.0f)
#define PIXEL_WIDTH 1184
#define PIXEL_HEIGHT 666
#define PIXEL_COUNT ((PIXEL_WIDTH/10) * (PIXEL_HEIGHT/10))
#define PIXEL_ASPECT_RATIO 1.777777777777778f
#define SHADOW_WIDTH 666
#define SHADOW_HEIGHT 666
#define HORIZ_BARS 66
#define VERT_BARS 66
#define HALF_HORIZ_BARS (HORIZ_BARS / 2)
#define HALF_VERT_BARS (VERT_BARS / 2)
#define BARS_COUNT (HORIZ_BARS * VERT_BARS)

#define ANTIALIASING
#define MSAA
// #define RAYTRACING
#define DEBUG

class GraphicsHandler {
public:
    mutex* pixelsMutex;

    vector<Block*>* blocks = new vector<Block*>();

    Camera* camera;

    float lightAngle = 0;
    float lightDistance = 20.0f;
    float lightSpeed = 0.0174533f;

    // Light position
    glm::vec3 lightPos;
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

    struct Sphere {
        glm::vec3 center;
        float radius;
        glm::vec3 color;
    };

    int numSpheres = 1; // Adjust the number of spheres as needed

    GraphicsHandler(mutex* pixelsMutex, vector<Block*>* blocks);
    void renderScene(ShaderProgram* shaderProgram);

    // Function to link a compute shader into a program
    GLuint linkComputeProgram(GLuint computeShader);

    void checkGLError(const char* stmt, const char* fname, int line);

#define GL_CHECK(stmt) do { \
    stmt; \
    checkGLError(#stmt, __FILE__, __LINE__); \
} while (0)

    void renderQuad();

#ifdef RAYTRACING
    void initRayTracing();
    void renderRayTracedScene();
    void cleanup(GLFWwindow* window);
#endif 

    // Function to initialize OpenGL settings
    void initGL();
    void initMSAA();
    void initFXAA();

    // Function to update shader uniforms
    void updateSceneUniforms();
    void updateDepthUniforms();

    void drawBlocks();

    // Main graphics rendering thread
    int graphicsThread(int argc, char* argv[]);
};
