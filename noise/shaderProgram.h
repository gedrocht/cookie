#pragma once
#include <string>
#include <cstring>
#include <iostream>
#include <fstream>
#include <sstream>
#include <glew.h>

using namespace std;

class ShaderProgram {
public:
    GLuint program;

    ShaderProgram();

    ShaderProgram(const char* vertexShaderPath, const char* fragmentShaderPath);

    void deleteShaders();

private:
    GLuint compiledVertexShader;
    GLuint compiledFragmentShader;

    string vertexShaderSource;
    string fragmentShaderSource;

    // Function to read shader source code from a file
    string readFile(const char* filePath);

    // Function to compile a shader from source code
    GLuint compileShader(const char* source, GLenum type);

    // Function to link shaders into a program
    GLuint linkProgram(GLuint vertexShader, GLuint fragmentShader);
};