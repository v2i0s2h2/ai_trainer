#!/bin/bash

# Configuration
IMAGE_NAME="vishnu202/ai-trainer-backend:latest"
CONTAINER_NAME="ai-trainer-backend"
PORT="8001"

echo "🚀 Starting local backend container..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found in current directory"
    exit 1
fi

# Stop and remove existing container if it exists
if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo "cleanup: Removing existing container ${CONTAINER_NAME}..."
    docker rm -f ${CONTAINER_NAME} > /dev/null
fi

# Run the container
echo "Running image: ${IMAGE_NAME} on port ${PORT}..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:${PORT} \
    --env-file .env \
    --restart unless-stopped \
    ${IMAGE_NAME}

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo "Logs: docker logs -f ${CONTAINER_NAME}"
    echo "Health: http://localhost:${PORT}/health"
else
    echo "❌ Failed to start container"
    exit 1
fi
