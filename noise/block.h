#pragma once
#include <cstdint>

class Block {
public:
    // Member variables
    float x;
    float y;
    float z;

    static const float size;
    static const float halfCubeSize;

    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;

    // Constructor
    Block(float xVal, float yVal, float zVal, uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal);

    // Default constructor
    Block();

    // Method to set position
    void setPosition(float xVal, float yVal, float zVal);

    // Method to set color
    void setColor(uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal);
};