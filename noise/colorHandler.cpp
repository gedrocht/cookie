#include "colorHandler.h"

// Function to convert HSL to RGB
unsigned int ColorHandler::HSLtoRGB(float hue, float saturation, float lightness) {
    float r, g, b;

    if (saturation == 0) {
        r = g = b = lightness;
    }
    else {
        auto hue2rgb = [](float p, float q, float t) {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 0.167f) return p + (q - p) * 6 * t;
            if (t < 0.500f) return q;
            if (t < 0.667f) return p + (q - p) * (0.667f - t) * 6;
            return p;
            };

        float q = lightness < 0.5 ? lightness * (1 + saturation) : lightness + saturation - lightness * saturation;
        float p = 2 * lightness - q;

        r = hue2rgb(p, q, hue + 0.333f);
        g = hue2rgb(p, q, hue);
        b = hue2rgb(p, q, hue - 0.333f);
    }

    unsigned int R = static_cast<unsigned int>(r * 255);
    unsigned int G = static_cast<unsigned int>(g * 255);
    unsigned int B = static_cast<unsigned int>(b * 255);

    return 0xFF000000 | (R << 16) | (G << 8) | B;
}

uint32_t ColorHandler::getColorFromData(uint32_t data) {
    static float hues[16] = {
            0.0f / 16,  1.0f / 16,  2.0f / 16,  3.0f / 16,
            4.0f / 16,  5.0f / 16,  6.0f / 16,  7.0f / 16,
            8.0f / 16,  9.0f / 16, 10.0f / 16, 11.0f / 16,
           12.0f / 16, 13.0f / 16, 14.0f / 16, 15.0f / 16
    };

    uint32_t volumeByte = (uint32_t)data;

    if ((volumeByte & 224) == 0) {
        volumeByte = 0;
    }
    /*
    if (volumeByte == 0) {
        throw(0);
    }
    */
    // volumeByte |= volumeByte >> 3;

    uint32_t frequencyByte = ((uint32_t)data) >> 8;

    // Determine the hue index
    int hueIndex = frequencyByte / 16;

    // Convert the hue to RGB with constant saturation and lightness
    float saturation = 1.0f;
    float lightness = 0.5f;

    uint32_t frequencyColor = HSLtoRGB(hues[hueIndex], saturation, lightness);

    uint32_t color = 0xFF000000 + (((uint32_t)volumeByte) << 16) + (((uint32_t)volumeByte) << 8) + ((uint32_t)volumeByte);

    color &= frequencyColor;

    return color;
}