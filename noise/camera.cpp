#include "camera.h"

using namespace std;

Camera::Camera() {
	// Camera position and direction
	this->xPosition = 46.4018f;
	this->yPosition = 142.5f;
	this->zPosition = 89.3235f;
	this->yRotation = -5.89561f;
	this->xRotation = 4.23407f;
	//this->camPitch = -2.77f;
	this->orbitSpeed = 0.000174533f * 20; // 0.01 degree in radians
	this->orbitDistance = 120.0f;
    this->orbitAngle = 0.0f; // Start angle for the orbit
}

void Camera::updateOrbit(float centerX, float centerY, float centerZ) {
    this->orbitAngle += this->orbitSpeed; // Update the angle for the orbit

    // Calculate new camera position using polar coordinates
    this->xPosition = centerX + orbitDistance * cos(orbitAngle);
    this->zPosition = centerZ + orbitDistance * sin(orbitAngle);
    this->yPosition = centerY; // Maintain the same height (or adjust as needed)

    // Ensure the camera is pointing at the center
    float cosCamPitch = cos(this->xRotation);
    glm::vec3 cameraPos = glm::vec3(this->xPosition, this->yPosition, this->zPosition);
    glm::vec3 cameraTarget = glm::vec3(centerX, centerY, centerZ);
    glm::vec3 up = glm::vec3(0.0f, 1.0f, 0.0f);
    glm::mat4 view = glm::lookAt(cameraPos, cameraTarget, up);
}