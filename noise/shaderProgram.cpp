#pragma once
#include "shaderProgram.h"

using namespace std;

ShaderProgram::ShaderProgram() {
    program = 0;
    compiledVertexShader = 0;
    compiledFragmentShader = 0;
    vertexShaderSource = "";
    fragmentShaderSource = "";
}

ShaderProgram::ShaderProgram(const char* vertexShaderPath, const char* fragmentShaderPath) {
    // Compile and link shaders
    // Read vertex and fragment shader source code from files
    vertexShaderSource = ShaderProgram::readFile(vertexShaderPath);
    fragmentShaderSource = ShaderProgram::readFile(fragmentShaderPath);
    // Compile vertex shader using the source code
    // GL_VERTEX_SHADER specifies that the shader is a vertex shader
    compiledVertexShader = ShaderProgram::compileShader(vertexShaderSource.c_str(), GL_VERTEX_SHADER);
    // Compile fragment shader using the source code
    // GL_FRAGMENT_SHADER specifies that the shader is a fragment shader
    compiledFragmentShader = ShaderProgram::compileShader(fragmentShaderSource.c_str(), GL_FRAGMENT_SHADER);
    // Link the compiled vertex and fragment shaders into a shader program
    program = linkProgram(compiledVertexShader, compiledFragmentShader);
}

void ShaderProgram::deleteShaders() {
    if (compiledVertexShader) {
        glDeleteShader(compiledVertexShader);
    }
    if (compiledFragmentShader) {
        glDeleteShader(compiledFragmentShader);
    }
}

// Function to read shader source code from a file
string ShaderProgram::readFile(const char* filePath) {
    ifstream file(filePath);
    if (!file.is_open()) {
        cerr << "Failed to open file: " << filePath << endl;
        return "";
    }
    stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

// Function to compile a shader from source code
GLuint ShaderProgram::compileShader(const char* source, GLenum type) {
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
GLuint ShaderProgram::linkProgram(GLuint vertexShader, GLuint fragmentShader) {
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