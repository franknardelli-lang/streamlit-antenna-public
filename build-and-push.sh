#!/bin/bash
# Build and push Docker image to Docker Hub
# Run this script from the project root directory

set -e  # Exit on error

DOCKER_USERNAME="franknardelli"
IMAGE_NAME="antenna-tools"
TAG="latest"

echo "🐳 Building Docker image..."
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} .

echo ""
echo "📤 Pushing to Docker Hub..."
echo "Please login to Docker Hub if prompted:"
docker login

docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}

echo ""
echo "✅ Image pushed successfully!"
echo "📦 Image: ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"
echo ""
echo "Next: Deploy to Azure Container Apps"
