#pragma once
#include <cstdint>
#include <glm.hpp>                  // For using OpenGL Mathematics library
#define GLM_ENABLE_EXPERIMENTAL     // For enabling experimental features in GLM
#include <gtc/matrix_transform.hpp> // For transformations such as translation, rotation, and scaling
#include <gtc/type_ptr.hpp>     // For converting GLM types to pointers

#include "shaderProgram.h"

class Block {
public:
    // Member variables
    float x;
    float y;
    float z;
    float distance;

    static const float size;
    static const float ninetyPercentSize;
    static const float halfCubeSize;

    Block(float xVal, float yVal, float zVal, uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal, float dVal);

    // Default constructor
    Block();

    // Method to set position
    void setPosition(float xVal, float yVal, float zVal);

    // Method to set color
    void setColor(uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal);

    void draw(ShaderProgram* shaderProgram, GLint* modelLoc, GLint* yScaleLoc, unsigned int* VAO);
private:
    uint8_t target_r;
    uint8_t target_g;
    uint8_t target_b;
    uint8_t target_a;

    uint8_t current_r;
    uint8_t current_g;
    uint8_t current_b;
    uint8_t current_a;
};