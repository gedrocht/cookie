cmake_minimum_required(VERSION 3.10)
project(Genten)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Include directories for Crow, Asio, JSON, CURL
include_directories(include/Crow/include)
include_directories(include/asio/include)
include_directories(include/json/include)
include_directories(include/curl/include)

# Find the CURL package
find_package(CURL REQUIRED)
include_directories(${CURL_INCLUDE_DIRS})

# Include pkg-config to help find packages
find_package(PkgConfig REQUIRED)

# Find the GLFW3 package using CMake's FindGLFW
find_package(glfw3 3.3 REQUIRED)

# Find the OpenGL package
find_package(OpenGL REQUIRED)
include_directories(${OPENGL_INCLUDE_DIR})

# GLAD: Optional, include if you need a modern OpenGL function loader
# Ensure you have glad.c and glad.h in your project or install it via CMake
# add_library(glad include/GLFW/glad/src/glad.c)
# include_directories(include/GLFW/glad/include)

# Add the GoogleTest subdirectory
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/release-1.10.0.tar.gz
)
FetchContent_MakeAvailable(googletest)

# Server library
add_library(server_lib server.cpp)
target_link_libraries(server_lib ${CURL_LIBRARIES})
target_include_directories(server_lib PRIVATE ${CURL_INCLUDE_DIRS})

# Main executable
add_executable(main main.cpp)
target_link_libraries(main server_lib pthread ${CURL_LIBRARIES} glfw ${OPENGL_LIBRARIES}) # glad

# Testing executable
enable_testing()
add_executable(main_test test.cpp)
target_link_libraries(main_test gtest_main server_lib pthread ${CURL_LIBRARIES})

include(GoogleTest)
gtest_discover_tests(main_test)
