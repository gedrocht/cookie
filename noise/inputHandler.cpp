#include "inputHandler.h"

#define KEYBOARD_INPUT
#define KEYBOARD_CONTROLS_CAMERA
#define KEYBOARD_CONTROLS_LIGHT
#define MOUSE_INPUT

using namespace std;

InputHandler::InputHandler() {}

InputHandler::InputHandler(GLFWwindow* window, Camera* camera) {
    this->window = window;
    this->camera = camera;
    glfwSetWindowUserPointer(window, this);
    glfwSetCursorPosCallback(window, InputHandler::mouseCallback);

    /*
    // If MOUSE_INPUT is defined, set the cursor position callback and hide the cursor
    // This callback is called whenever the mouse moves
    glfwSetCursorPosCallback(window, this->mouseCallback);
    // Hide the cursor and capture it within the window
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    */
}

void InputHandler::mouseCallback(GLFWwindow* window, double xpos, double ypos) {
    // Get the pointer to the InputHandler instance from the window user pointer
    InputHandler* handler = static_cast<InputHandler*>(glfwGetWindowUserPointer(window));
    if (handler) {
        handler->handleMouseCallback(xpos, ypos);
    }
}

void InputHandler::handleMouseCallback(double xpos, double ypos) {
    // todo we aren't actually using xpos and ypos and that's probably very wrong
    static double lastX = camera->xPosition;
    static double lastY = camera->yPosition;
    double xoffset = camera->xPosition - lastX;
    double yoffset = lastY - camera->yPosition; // Reversed since y-coordinates range from bottom to top
    lastX = camera->xPosition;
    lastY = camera->yPosition;

    xoffset *= sensitivity;
    yoffset *= sensitivity;

    camera->yRotation -= xoffset;
    camera->xRotation -= yoffset;

    cout << "camera yRotation: " << camera->yRotation << ", camera xRotation: " << camera->xRotation << endl;

    if (camera->xRotation > 89.0f) {
        camera->xRotation = 89.0f;
    }
    else if (camera->xRotation < -89.0f) {
        camera->xRotation = -89.0f;
    }
}

// Function to handle keyboard input for camera movement
void InputHandler::processInput() {
    float _camX = camera->xPosition;
    float _camY = camera->yPosition;
    float _camZ = camera->zPosition;

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
        camera->xPosition -= speed * sin(camera->yPosition);
        camera->zPosition -= speed * cos(camera->yPosition);
    }
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
        camera->xPosition += speed * sin(camera->yPosition);
        camera->zPosition += speed * cos(camera->yPosition);
    }
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
        camera->xPosition -= speed * cos(camera->yPosition);
        camera->zPosition += speed * sin(camera->yPosition);
    }
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
        camera->xPosition += speed * cos(camera->yPosition);
        camera->zPosition -= speed * sin(camera->yPosition);
    }
    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS) {
        camera->yPosition += speed;
    }
    if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS) {
        camera->yPosition -= speed;
    }

    if (camera->xPosition != _camX || camera->yPosition != _camY || camera->zPosition != _camZ) {
        cout << "cam: " << camera->xPosition << ", " << camera->yPosition << ", " << camera->zPosition << endl;
    }
}