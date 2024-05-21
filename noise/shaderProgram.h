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

    // Function to read shader source code from a file
    static string readFile(const char* filePath);

    // Function to compile a shader from source code
    static GLuint compileShader(const char* source, GLenum type);
private:
    GLuint compiledVertexShader;
    GLuint compiledFragmentShader;

    string vertexShaderSource;
    string fragmentShaderSource;

    // Function to link shaders into a program
    GLuint linkProgram(GLuint vertexShader, GLuint fragmentShader);
};