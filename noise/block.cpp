#include "block.h"

// Definition of static members
const float Block::size = 1.5f;
const float Block::halfCubeSize = Block::size / 2;

// Constructor
Block::Block(float xVal, float yVal, float zVal, uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal)
    : x(xVal), y(yVal), z(zVal), r(rVal), g(gVal), b(bVal), a(aVal) {}

// Default constructor
Block::Block() : x(0), y(0), z(0), r(0), g(0), b(0), a(255) {} // Default to fully opaque white

// Method to set position
void Block::setPosition(float xVal, float yVal, float zVal) {
    x = xVal;
    y = yVal;
    z = zVal;
}

// Method to set color
void Block::setColor(uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal) {
    r = rVal;
    g = gVal;
    b = bVal;
    a = aVal;
}