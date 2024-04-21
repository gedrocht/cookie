cmake_minimum_required(VERSION 3.10)
project(Genten)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Include directories for Crow and Asio
include_directories(include/Crow/include)
include_directories(include/asio/include)
include_directories(include/json/include)

# Add the GoogleTest subdirectory
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/release-1.10.0.tar.gz
)
FetchContent_MakeAvailable(googletest)

# Server library
add_library(server_lib server.cpp)

# Main executable
add_executable(api_server api_server.cpp)
target_link_libraries(api_server server_lib pthread)

# Testing executable
enable_testing()
add_executable(api_server_test test.cpp)
target_link_libraries(api_server_test gtest_main server_lib pthread)

include(GoogleTest)
gtest_discover_tests(api_server_test)
