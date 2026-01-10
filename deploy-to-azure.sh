#!/bin/bash
# Deploy to Azure Container Apps (Build -> Push -> Deploy)
# Prerequisites: Docker running, Azure CLI logged in

set -e  # Exit on error

# Configuration
DOCKER_USERNAME="franknardelli"
IMAGE_NAME="antenna-tools"
TAG="latest"
RESOURCE_GROUP="antenna-tools-rg"
LOCATION="eastus"
APP_NAME="antenna-tools"
CONTAINER_APP_ENV="antenna-env"

echo "🚀 Starting Deployment: Build -> Push -> Deploy"
echo "============================================="

# 1. Check Azure Login
echo "📋 Checking Azure login..."
az account show > /dev/null 2>&1 || {
    echo "❌ Not logged into Azure. Please run: az login"
    exit 1
}
echo "✅ Azure login confirmed"
echo ""

# 2. Build Docker Image
echo "🐳 Building Docker image..."
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} .
echo "✅ Build complete"
echo ""

# 3. Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} || {
    echo "❌ Push failed. Please run 'docker login' and try again."
    exit 1
}
echo "✅ Push complete"
echo ""

# Create Container Apps environment if it doesn't exist
echo "📦 Creating Container Apps environment (if needed)..."
az containerapp env create \
  --name ${CONTAINER_APP_ENV} \
  --resource-group ${RESOURCE_GROUP} \
  --location ${LOCATION} \
  --output table 2>/dev/null || echo "Environment already exists"

echo ""
echo "🚢 Deploying container app..."
az containerapp create \
  --name ${APP_NAME} \
  --resource-group ${RESOURCE_GROUP} \
  --environment ${CONTAINER_APP_ENV} \
  --image docker.io/${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} \
  --target-port 8501 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 2 \
  --output table 2>/dev/null || {
    echo "App already exists, updating..."
    az containerapp update \
      --name ${APP_NAME} \
      --resource-group ${RESOURCE_GROUP} \
      --image docker.io/${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} \
      --min-replicas 0 \
      --max-replicas 2 \
      --output table
}

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Getting your app URL..."
APP_URL=$(az containerapp show \
  --name ${APP_NAME} \
  --resource-group ${RESOURCE_GROUP} \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo ""
echo "======================================"
echo "🎉 Your app is live at:"
echo "https://${APP_URL}"
echo "======================================"
echo ""
