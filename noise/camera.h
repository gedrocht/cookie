#pragma once
#include <cmath>

class Camera {
public:
	// Camera position and direction
	float xPosition;
	float yPosition;
	float zPosition;
	float yRotation;
	float xRotation;
	float orbitSpeed;
	float orbitDistance;

	Camera();


	// Make the camera orbit
	void rotateAroundCenter(float xCenter, float zCenter);
};