#pragma once
#include <stdint.h>

static class ColorHandler {
public:
    // Function to convert HSL to RGB
    static unsigned int HSLtoRGB(float hue, float saturation, float lightness);

    static uint32_t getColorFromData(uint32_t data);
};