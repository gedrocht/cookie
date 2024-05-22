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
	this->orbitSpeed = 0.000174533f * 5; // 0.01 degree in radians
	this->orbitDistance = 120.0f;
}

void Camera::rotateAroundCenter(float xCenter, float zCenter) {
	float newAngle = -1 * (yRotation - 1.65f);
	xPosition = orbitDistance * cos(newAngle) + xCenter;
	zPosition = orbitDistance * sin(newAngle) + zCenter;
	yRotation -= orbitSpeed;

	if (yRotation < 0) {
		yRotation += 6.28318f;
	}
}