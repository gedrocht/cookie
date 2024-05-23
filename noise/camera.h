#pragma once
#include <cmath>
#include <glm.hpp>              // For using OpenGL Mathematics library
#include <gtc/matrix_transform.hpp> // For transformations such as translation, rotation, and scaling

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
	float orbitAngle;

	Camera();

	void updateOrbit(float centerX, float centerY, float centerZ);
};