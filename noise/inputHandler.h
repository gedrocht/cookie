#pragma once
#include <glfw3.h>              // For creating windows with OpenGL contexts and handling input/events
#include <iostream>
#include "camera.h"

class InputHandler {
public:
    // Constants for movement speed and mouse sensitivity
    const float speed = 0.25f;
    const float sensitivity = 0.0005f;
    GLFWwindow* window;
    Camera* camera;
    InputHandler();
    InputHandler(GLFWwindow* window, Camera* camera);
    static void mouseCallback(GLFWwindow* window, double xpos, double ypos);
    void handleMouseCallback(double xpos, double ypos);
    void processInput();
};