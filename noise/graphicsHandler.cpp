#include "graphicsHandler.h"

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

GraphicsHandler::GraphicsHandler(mutex* pixelsMutex, vector<Block*>* blocks) {
    this->lightPos = glm::vec3(-40.0f, 300.0f, 100.0f);
    this->pixelsMutex = pixelsMutex;
    this->blocks = blocks;
    this->lightAngle = 0;
    this->lightDistance = 20.0f;
    this->lightSpeed = 0.0174533f;
    this->numSpheres = 1;
}

#ifdef RAYTRACING
// Function to link a compute shader into a program
GLuint GraphicsHandler::linkComputeProgram(GLuint computeShader) {
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
#endif

void GraphicsHandler::checkGLError(const char* stmt, const char* fname, int line) {
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

void GraphicsHandler::renderQuad() {
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

void GraphicsHandler::initMSAA() {
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
}

void GraphicsHandler::initFXAA() {
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
}

void GraphicsHandler::initShadows() {
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
}

// Function to initialize OpenGL settings
void GraphicsHandler::initGL() {
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

    initShadows();

#ifdef ANTIALIASING
#ifdef MSAA
    initMSAA();
#endif
    initFXAA();
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

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
#ifdef MSAA
    glEnable(GL_MULTISAMPLE);  // Enable MSAA
#endif
    glEnable(GL_DEBUG_OUTPUT);
    glDebugMessageCallback([](GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar* message, const void* userParam) {
        std::cerr << "GL ERROR: " << message << std::endl;
        }, nullptr);
#ifdef RAYTRACING
    initRayTracing();
#endif
}

// Function to update shader uniforms
void GraphicsHandler::updateSceneUniforms() {
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

void GraphicsHandler::updateDepthUniforms() {
    glm::mat4 lightSpaceMatrix = glm::mat4(1.0f); // Placeholder, should be calculated based on light's view/projection matrices
    glm::mat4 model = glm::mat4(1.0f);

    glUseProgram(depthShaderProgram->program);
    GLint lightSpaceMatrixLocDepth = glGetUniformLocation(depthShaderProgram->program, "lightSpaceMatrix");
    GLint modelLocDepth = glGetUniformLocation(depthShaderProgram->program, "model");

    glUniformMatrix4fv(lightSpaceMatrixLocDepth, 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));
    glUniformMatrix4fv(modelLocDepth, 1, GL_FALSE, glm::value_ptr(model));
}

void GraphicsHandler::drawBlocks() {
    // Lock the mutex to safely access the pixel data
    std::lock_guard<std::mutex> guard(*pixelsMutex);
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
        }
    }
    for (int i = 0; i < blocks->size(); i++) {
        blocks->at(i)->draw(sceneShaderProgram, &modelLoc, &yScaleLoc, &VAO);
    }
}

void GraphicsHandler::processAntiAliasing() {
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

void GraphicsHandler::setUpSceneForMSAA() {
    // Bind the MSAA framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, msaaFBO);
    // Clear the color and depth buffers to prepare for new frame rendering
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

// Function to render the scene
// This function is responsible for rendering the entire scene using the specified shader program
void GraphicsHandler::renderScene(ShaderProgram* shaderProgram) {
#ifdef ANTIALIASING
#ifdef MSAA
    // Bind the MSAA framebuffer to start rendering with multisample anti-aliasing
    if (shaderProgram == sceneShaderProgram) {
        setUpSceneForMSAA();
    }
#endif
#endif
    glViewport(0, 0, PIXEL_WIDTH, PIXEL_HEIGHT);
    // Clear the color and depth buffers to prepare for rendering the scene
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // Use the specified shader program for rendering
    glUseProgram(shaderProgram->program);

    if (shaderProgram == sceneShaderProgram) {
        updateSceneUniforms();
    }
    else if (shaderProgram == depthShaderProgram) {
        updateDepthUniforms();
    }

    drawBlocks();

#ifdef ANTIALIASING
    if (shaderProgram == sceneShaderProgram) {
        processAntiAliasing();
    }
#endif
}

// Function to handle window resize
void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    glViewport(0, 0, width, height);
}

void GraphicsHandler::calculateShadows() {
    // Clear the color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    // 1. Render depth map from light's perspective
    // Set the viewport to the size of the shadow map
    glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT);
    // Bind the framebuffer for depth map rendering
    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
    // Clear the depth buffer to prepare for new depth data
    glClear(GL_DEPTH_BUFFER_BIT);
    // Render the scene using the depth shader program
    renderScene(depthShaderProgram);
    // Unbind the framebuffer to return to the default framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    // 2. Render scene with shadows
}

int GraphicsHandler::initializeGraphics() {
    camera = new Camera();

    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
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

    window = glfwCreateWindow(PIXEL_WIDTH, PIXEL_HEIGHT, "Pixels", NULL, NULL);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW" << std::endl;
        return -1;
    }

    initGL();

    return 0;
}

void GraphicsHandler::update() {
    glfwPollEvents();
#ifdef RAYTRACING
    renderRayTracedScene();
#else
    calculateShadows();
    renderScene(sceneShaderProgram);
#endif
    // Swap front and back buffers
    // This displays the rendered image on the screen
    glfwSwapBuffers(window);
    // Wait for the specified frame delay
    // This controls the frame rate by pausing for a specified amount of time
    glfwWaitEventsTimeout(FRAME_DELAY_IN_SECONDS);
}

void GraphicsHandler::cleanup() {
    // Clean up and terminate GLFW
    // Destroy the window and free associated resources
    glfwDestroyWindow(window);
    // Terminate GLFW and free any remaining resources
    glfwTerminate();
#ifdef RAYTRACING
    cleanupRayTracing(window);
#endif
}

// Main graphics rendering thread
int GraphicsHandler::graphicsThread(int argc, char* argv[]) {
    if (initializeGraphics() != 0) {
        return -1;
    }

    while (!glfwWindowShouldClose(window)) {
        update();
    }
    
    cleanup();

    return 0;  // Return success code indicating the program ended without errors
}

#ifdef RAYTRACING
void GraphicsHandler::initRayTracing() {
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

void GraphicsHandler::renderRayTracedScene() {
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

void GraphicsHandler::cleanupRayTracing(GLFWwindow* window) {
    glDeleteProgram(rayTracingShaderProgram);
    glDeleteBuffers(1, &ssboSpheres);
    glDeleteBuffers(1, &ssboResult);
    glDeleteTextures(1, &resultTexture);
    glfwDestroyWindow(window);
    glfwTerminate();
}
#endif 