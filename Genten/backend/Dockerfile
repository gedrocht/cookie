# Use an official Ubuntu base image
FROM ubuntu:20.04

# Avoid user interaction with tzdata, etc.
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    pkg-config \
    libglfw3 \
    libglfw3-dev \
    libglew-dev \
    libcurl4-openssl-dev \
    mesa-utils \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set the working directory inside the container
WORKDIR /backend

# Copy the current directory contents into the container at /backend
COPY . /backend

# Use CRLF line endings in case of Windows builds
RUN apt-get update && apt-get install -y dos2unix \
    && find /backend -type f -print0 | xargs -0 dos2unix \
    && apt-get --purge remove -y dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Build the application
RUN mkdir -p build \
    && cd build \
    && cmake .. \
    && make

# Reset the default shell to avoid any script issues with sh vs bash
SHELL ["/bin/bash", "-c"]
