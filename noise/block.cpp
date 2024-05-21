#include "block.h"

// Definition of static members
const float Block::size = 1.5f;
const float Block::ninetyPercentSize = Block::size * 0.9f;
const float Block::halfCubeSize = Block::size / 2;

// Constructor
Block::Block(float xVal, float yVal, float zVal, uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal, float dVal)
    : x(xVal), y(yVal), z(zVal), current_r(rVal), current_g(gVal), current_b(bVal), current_a(aVal), 
      target_r(rVal), target_g(gVal), target_b(bVal), target_a(aVal),  distance(dVal) {}

// Default constructor
Block::Block() {
    this->current_r = 0;
    this->current_g = 0;
    this->current_b = 0;
    this->current_a = 0;
    this->target_r = 0;
    this->target_g = 0;
    this->target_b = 0;
    this->target_a = 0;
    this->x = 0;
    this->y = 0;
    this->z = 0;
    this->distance = 0;
}

// Method to set position
void Block::setPosition(float xVal, float yVal, float zVal) {
    this->x = xVal;
    this->y = yVal;
    this->z = zVal;
}

// Method to set color
void Block::setColor(uint8_t rVal, uint8_t gVal, uint8_t bVal, uint8_t aVal) {
    this->target_r = rVal;
    this->target_g = gVal;
    this->target_b = bVal;
    this->target_a = aVal;
}

int get_tween(int current, int target) {
    if (current < target) {
        return (target - current) / 5;
    }
    else if (current > target) {
        return -1 * ((current - target) / 5);
    }
    return 0;
}

void Block::draw(ShaderProgram *shaderProgram, GLint* modelLoc, GLint* yScaleLoc, unsigned int* VAO) {
    if (this->target_r + this->target_b + this->target_g == 0) {
        return;
    }
    // Calculate brightness as the average of the RGB values
    //current_r = (uint8_t)(((float)current_r + (float)target_r) / 2.0f);
    //current_g = (uint8_t)(((float)current_g + (float)target_g) / 2.0f);

    //if (this->current_b != this->target_b) {
      

    int r_tween = get_tween(current_r, target_r);
    int g_tween = get_tween(current_g, target_g);
    int b_tween = get_tween(current_b, target_b);

    if (abs(r_tween) < 1) {
        this->current_r = this->target_r;
        r_tween = 0;
    }
    if (abs(g_tween) < 1) {
        this->current_g = this->target_g;
        g_tween = 0;
    }
    if (abs(b_tween) < 1) {
        this->current_b = this->target_b;
        b_tween = 0;
    }

    this->current_r += r_tween;
    this->current_g += g_tween;
    this->current_b += b_tween;

    /*
    this->current_r = this->target_r;
    this->current_g = this->target_g;
    this->current_b = this->target_b;
    this->current_a = this->target_a;
    */

        /*
        //this->current_b = (this->current_b + this->target_b) / 2;
        if (this->current_b < this->target_b) {
            this->current_b++;
        }
        else if (this->current_b > this->target_b) {
            __noop;
            //this->current_b--;
        }
        */
    //}
    // float a = (a + target_a) / 2.0f;
    float current_brightness = (this->current_r + this->current_g + this->current_b) / 765.0f;

    // Use brightness to scale the y-axis size
    float current_yScale = 1.0f + current_brightness * 50.0f;

    glm::mat4 model = glm::mat4(1.0f);
    model = glm::translate(model, glm::vec3(this->x, this->y, this->z));
    model = glm::scale(model, glm::vec3(ninetyPercentSize, ninetyPercentSize, ninetyPercentSize));

    // Convert RGBA values to [0,1] range
    glm::vec4 current_color = glm::vec4(
        this->current_r / 255.0f,
        this->current_g / 255.0f,
        this->current_b / 255.0f,
        this->current_a / 255.0f);

    glUseProgram(shaderProgram->program);
    glUniformMatrix4fv(*modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glUniform1f(*yScaleLoc, current_yScale);
    glUniform3fv(glGetUniformLocation(shaderProgram->program, "cubeColor"), 1, glm::value_ptr(current_color)); // Pass the color

    glBindVertexArray(*VAO); // Bind the VAO
    glDrawArrays(GL_TRIANGLES, 0, 36); // Draw the cube
    glBindVertexArray(0); // Unbind the VAO
}