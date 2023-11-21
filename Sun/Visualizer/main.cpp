#define GLEW_STATIC
#include <glew.h>
#include <glfw3.h>
#include <vector>

struct Point3D {
    float x, y, z;
};

int main() {
    std::vector<Point3D> cubeVertices = {
        {-1.0f, -1.0f, -1.0f}, // Vertex 0
        { 1.0f, -1.0f, -1.0f}, // Vertex 1
        { 1.0f,  1.0f, -1.0f}, // Vertex 2
        {-1.0f,  1.0f, -1.0f}, // Vertex 3
        {-1.0f, -1.0f,  1.0f}, // Vertex 4
        { 1.0f, -1.0f,  1.0f}, // Vertex 5
        { 1.0f,  1.0f,  1.0f}, // Vertex 6
        {-1.0f,  1.0f,  1.0f}  // Vertex 7
    };

  if (!glfwInit()) {
      // Initialization failed
      return -1;
  }

  GLFWwindow* window = glfwCreateWindow(640, 480, "3D Points Display", NULL, NULL);
  if (!window) {
      glfwTerminate();
      return -1;
  }
  glfwMakeContextCurrent(window);

  glewExperimental = true; 
  if (glewInit() != GLEW_OK) {
    // GLEW initialization failed
    glfwTerminate();
   return -1;
  }

    while (!glfwWindowShouldClose(window)) {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Render cube
        glBegin(GL_LINES);
        for (int i = 0; i < 4; ++i) { // Draw bottom face
            glVertex3f(cubeVertices[i].x, cubeVertices[i].y, cubeVertices[i].z);
            glVertex3f(cubeVertices[(i + 1) % 4].x, cubeVertices[(i + 1) % 4].y, cubeVertices[(i + 1) % 4].z);
        }
        for (int i = 0; i < 4; ++i) { // Draw top face
            glVertex3f(cubeVertices[i + 4].x, cubeVertices[i + 4].y, cubeVertices[i + 4].z);
            glVertex3f(cubeVertices[(i + 1) % 4 + 4].x, cubeVertices[(i + 1) % 4 + 4].y, cubeVertices[(i + 1) % 4 + 4].z);
        }
        for (int i = 0; i < 4; ++i) { // Connect top and bottom faces
            glVertex3f(cubeVertices[i].x, cubeVertices[i].y, cubeVertices[i].z);
            glVertex3f(cubeVertices[i + 4].x, cubeVertices[i + 4].y, cubeVertices[i + 4].z);
        }
        glEnd();

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

  glfwDestroyWindow(window);
  glfwTerminate();
}