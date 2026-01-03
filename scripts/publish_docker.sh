#!/bin/bash
set -e

# Docker Hub Username
DOCKER_USER="vishnu202"

if [ -z "$DOCKER_USER" ]; then
    echo "Error: Username is required."
    exit 1
fi

IMAGE_NAME="$DOCKER_USER/ai-trainer-backend"

echo "🐳 Building lean backend image for linux/amd64..."
# Build using Dockerfile.backend and enforce platform for Intel home server
docker build --platform linux/amd64 -f Dockerfile.backend -t $IMAGE_NAME:latest .

echo "🔑 Logging in to Docker Hub..."
docker login

echo "🚀 Pushing image to Docker Hub..."
docker push $IMAGE_NAME:latest

echo "✅ Done! Image pushed to: $IMAGE_NAME:latest"
echo "Update docker-compose.release.yml with this image name."
