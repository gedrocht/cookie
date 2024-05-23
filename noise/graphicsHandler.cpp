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
ShaderProgram* sceneShaderProgram;

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
    this->lightPos = glm::vec3(-40.0f, 100.0f, 100.0f);
    this->lightPos = glm::vec3(-40, 80, 0);
    this->pixelsMutex = pixelsMutex;
    this->blocks = blocks;
    this->lightAngle = 0;
    this->lightDistance = 100.0f;
    this->lightSpeed = 0.0174533f;
    this->numSpheres = 1;
}

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
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
        std::cerr << "Framebuffer not complete!" << std::endl;
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void GraphicsHandler::calculateShadows() {
    glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT);
    glBindFramebuffer(GL_FRAMEBUFFER, depthMapFBO);
    glClear(GL_DEPTH_BUFFER_BIT);
    renderScene(sceneShaderProgram);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glViewport(0, 0, PIXEL_WIDTH, PIXEL_HEIGHT);
}

// Function to initialize OpenGL settings
void GraphicsHandler::initGL() {
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
}

void GraphicsHandler::initReflectionRefraction() {
    // Reflection FBO
    glGenFramebuffers(1, &reflectionFBO);
    glGenTextures(1, &reflectionTexture);
    glBindTexture(GL_TEXTURE_2D, reflectionTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, PIXEL_WIDTH, PIXEL_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glBindFramebuffer(GL_FRAMEBUFFER, reflectionFBO);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, reflectionTexture, 0);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);

    // Refraction FBO
    glGenFramebuffers(1, &refractionFBO);
    glGenTextures(1, &refractionTexture);
    glBindTexture(GL_TEXTURE_2D, refractionTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, PIXEL_WIDTH, PIXEL_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glBindFramebuffer(GL_FRAMEBUFFER, refractionFBO);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, refractionTexture, 0);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void GraphicsHandler::renderReflectionTexture() {
    // Set up reflection camera
    reflectionCamera->xPosition = mainCamera->xPosition;
    reflectionCamera->yPosition = -mainCamera->yPosition; // Reflect the y position
    reflectionCamera->zPosition = mainCamera->zPosition;
    reflectionCamera->yRotation = mainCamera->yRotation;
    reflectionCamera->xRotation = -mainCamera->xRotation; // Reflect the x rotation

    glBindFramebuffer(GL_FRAMEBUFFER, reflectionFBO);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glUseProgram(sceneShaderProgram->program);
    updateSceneUniforms(reflectionCamera);
    drawBlocks();
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void GraphicsHandler::renderRefractionTexture() {
    // Set up refraction camera (similar to the main camera, but adjusted as needed)
    refractionCamera->xPosition = mainCamera->xPosition;
    refractionCamera->yPosition = mainCamera->yPosition;
    refractionCamera->zPosition = mainCamera->zPosition;
    refractionCamera->yRotation = mainCamera->yRotation;
    refractionCamera->xRotation = mainCamera->xRotation;

    glBindFramebuffer(GL_FRAMEBUFFER, refractionFBO);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glUseProgram(sceneShaderProgram->program);
    updateSceneUniforms(refractionCamera);
    drawBlocks();
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

GLuint GraphicsHandler::loadCubemap(std::vector<std::string> faces) {
    GLuint textureID;
    glGenTextures(1, &textureID);
    glBindTexture(GL_TEXTURE_CUBE_MAP, textureID);

    int width, height, nrChannels;
    for (GLuint i = 0; i < faces.size(); i++) {
        unsigned char* data = stbi_load(faces[i].c_str(), &width, &height, &nrChannels, 0);
        if (data) {
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data
            );
            stbi_image_free(data);
        }
        else {
            std::cout << "Cubemap texture failed to load at path: " << faces[i] << std::endl;
            stbi_image_free(data);
        }
    }
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);

    return textureID;
}

glm::mat4 GraphicsHandler::calculateLightSpaceMatrix() {
    glm::mat4 lightProjection, lightView;
    float near_plane = 1.0f, far_plane = 1000.0f;
    lightProjection = glm::ortho(-333.0f, 333.0f, -333.0f, 333.0f, near_plane, far_plane);
    lightView = glm::lookAt(lightPos, glm::vec3(0.0f, 0.0f, 0.0f), glm::vec3(0.0, 1.0, 0.0));
    return lightProjection * lightView;
}

// Function to update shader uniforms
void GraphicsHandler::updateSceneUniforms(Camera* camera) {
    glm::mat4 model = glm::mat4(1.0f);

    // Calculate the camera direction based on xRotation and yRotation
    float cosCamPitch = cos(camera->xRotation);
    glm::vec3 cameraFront = glm::vec3(
        cosCamPitch * sin(camera->yRotation),
        sin(camera->xRotation),
        cosCamPitch * cos(camera->yRotation)
    );
    glm::vec3 cameraPos = glm::vec3(camera->xPosition, camera->yPosition, camera->zPosition);
    glm::vec3 cameraTarget = cameraPos + cameraFront;
    glm::vec3 up = glm::vec3(0.0f, 1.0f, 0.0f);

    // Create the view matrix using the camera position and direction
    glm::mat4 view = glm::lookAt(cameraPos, cameraTarget, up);

    glm::mat4 projection = glm::perspective(0.785398f, PIXEL_ASPECT_RATIO, 0.1f, 1000.0f);
    glm::mat4 lightSpaceMatrix = calculateLightSpaceMatrix();

    glUseProgram(sceneShaderProgram->program);
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
    glUniformMatrix4fv(projectionLoc, 1, GL_FALSE, glm::value_ptr(projection));
    glUniform3fv(lightPosLoc, 1, glm::value_ptr(lightPos));
    glUniform3fv(viewPosLoc, 1, glm::value_ptr(cameraPos));
    glUniformMatrix4fv(lightSpaceMatrixLoc, 1, GL_FALSE, glm::value_ptr(lightSpaceMatrix));

    // Bind shadow map texture
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, shadowMap);
    glUniform1i(glGetUniformLocation(sceneShaderProgram->program, "shadowMap"), 0);

    // Bind reflection and refraction textures
    glActiveTexture(GL_TEXTURE1);
    glBindTexture(GL_TEXTURE_2D, reflectionTexture);
    glUniform1i(glGetUniformLocation(sceneShaderProgram->program, "reflectionTexture"), 1);

    glActiveTexture(GL_TEXTURE2);
    glBindTexture(GL_TEXTURE_2D, refractionTexture);
    glUniform1i(glGetUniformLocation(sceneShaderProgram->program, "refractionTexture"), 2);

    // Bind environment map texture
    glActiveTexture(GL_TEXTURE3);
    glBindTexture(GL_TEXTURE_CUBE_MAP, envMap);
    glUniform1i(glGetUniformLocation(sceneShaderProgram->program, "envMap"), 3);
}

void GraphicsHandler::drawBlocks() {
    // Lock the mutex to safely access the pixel data
    std::lock_guard<std::mutex> guard(*pixelsMutex);
    auto block_iterator = blocks->begin();
    uint32_t color = 0;
    int pixelIndex = 0;
    glm::vec3 camPositionVec3 = glm::vec3(mainCamera->xPosition, mainCamera->yPosition, mainCamera->zPosition);
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
        updateSceneUniforms(mainCamera);
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

int GraphicsHandler::initializeGraphics() {
    mainCamera = new Camera();
    reflectionCamera = new Camera();
    refractionCamera = new Camera();

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

void GraphicsHandler::initEnvironmentMap() {
    std::vector<std::string> faces{
        "right.jpg",
        "left.jpg",
        "top.jpg",
        "bottom.jpg",
        "front.jpg",
        "back.jpg"
    };
    envMap = loadCubemap(faces);
}

void GraphicsHandler::updateLightOrbit(float centerX, float centerY, float centerZ) {
    static float orbitAngle = 0.0f;
    static float orbitSpeed = 0.03f;
    static float orbitDistance = 120.0f;
    orbitAngle += orbitSpeed; // Update the angle for the orbit
    if (orbitAngle > 6.283185307) {
        orbitAngle -= 6.283185307;
    }
    
    lightPos[0] = centerX + orbitDistance * cos(orbitAngle);
    lightPos[1] = centerY; // Maintain the same height (or adjust as needed)
    lightPos[2] = centerZ + orbitDistance * sin(orbitAngle);
}

void GraphicsHandler::update(int* currentIndex) {
    glfwPollEvents();

    // mainCamera->updateOrbit(0, 142.5f, 0);
    // updateLightOrbit(0, 142.5f, 0);
    /*
    float newTarget = (*currentIndex / VERT_BARS) * Block::size - (float)(HALF_VERT_BARS);
    float difference = newTarget - lightPos[2];
    if (abs(difference) > 10.0f) {

    }
    lightPos[2] = (lightPos[2] * 9.0f + newTarget) / 10.0f;
    */

    renderReflectionTexture();
    renderRefractionTexture();
    calculateShadows();
    renderScene(sceneShaderProgram);
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
}

// Main graphics rendering thread
int GraphicsHandler::graphicsThread(int argc, char* argv[], int* currentIndex) {
    if (initializeGraphics() != 0) {
        return -1;
    }

    while (!glfwWindowShouldClose(window)) {
        update(currentIndex);
    }

    cleanup();

    return 0;  // Return success code indicating the program ended without errors
}