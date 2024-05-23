#pragma once
#include <algorithm>            // For sort funcionality
#include <iostream>             // For standard input/output operations
#include <bitset>               // For manipulating bits and performing bitwise operations
#include <fstream>              // For file input/output operations
#include <sstream>              // For string stream operations
#include <thread>               // For multithreading support
#include <mutex>                // For mutual exclusion to prevent race conditions
#include <vector>               // For using the vector container from the standard library
#include <cstring>              // For manipulating C-style strings
#include <cstdlib>              // For general utilities including dynamic memory management
#include <glew.h>               // For managing OpenGL extensions
#include <glfw3.h>              // For creating windows with OpenGL contexts and handling input/events
#include <glm.hpp>              // For using OpenGL Mathematics library
#define GLM_ENABLE_EXPERIMENTAL // For enabling experimental features in GLM
#include <gtc/matrix_transform.hpp> // For transformations such as translation, rotation, and scaling
#include <gtc/type_ptr.hpp>     // For converting GLM types to pointers
#include <gtx/string_cast.hpp>  // For converting GLM types to strings

#include "block.h"
#include "shaderProgram.h"
#include "camera.h"
#include "colorHandler.h"
#include "clientHandler.h"
#include "inputHandler.h"
#include "graphicsHandler.h"

using namespace std;

vector<Block*>* blocks = new vector<Block*>();

size_t currentIndex = 0;
mutex pixelsMutex;

InputHandler* inputHandler;
GraphicsHandler* graphicsHandler;

int graphicsThread(int argc, char* argv[], int* currentIndex) {
    return graphicsHandler->graphicsThread(argc, argv, currentIndex);
}

// Main function
int main(int argc, char* argv[]) {
    static int numClients = 0;
    for (int i = 0; i < BARS_COUNT; i++) {
        blocks->push_back(new Block());
    }

    graphicsHandler = new GraphicsHandler(&pixelsMutex, blocks);

    // Create a thread for the graphics rendering
    thread gThread(graphicsThread, argc, argv, reinterpret_cast<int*>(&currentIndex));
    ClientHandler<Block>* clientHandler = new ClientHandler<Block>(&pixelsMutex, blocks, BARS_COUNT, reinterpret_cast<int*>(&currentIndex), &numClients);
    clientHandler->initialize();

    gThread.join();
    return 0;
}
