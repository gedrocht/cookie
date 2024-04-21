# Start from the official Ubuntu image
FROM ubuntu:20.04

# Install necessary packages
RUN apt-get update && apt-get install -y g++ cmake libglfw3 libglfw3-dev libglew-dev

# Copy the backend directory
WORKDIR /backend
COPY . /backend

# Build the application
RUN mkdir -p build && cd build && cmake .. && make

# Run the API server
CMD ["./build/api_server"]
