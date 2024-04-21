# Start from the official Ubuntu image
FROM ubuntu:20.04

# Avoid timezone configuration interaction
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    libglfw3 \
    libglfw3-dev \
    libglew-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the CMake and other necessary build files first
COPY CMakeLists.txt /app/
# If you have other configuration or scripts needed for CMake, copy them here

# Optional ARG for controlling the build process
ARG CLEAN_BUILD=false

# Conditionally remove build directory based on the argument
RUN if [ "${CLEAN_BUILD}" = "true" ] ; then rm -rf ./build ; fi

# Prepare build directory and run cmake to configure the project
COPY . /app

# Copy the rest of the source code
RUN mkdir -p build && cd build && cmake ..

# Build the application
RUN make && ls -la

# Run the API server
CMD ["./api_server"]
