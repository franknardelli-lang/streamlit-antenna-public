#!/bin/bash
# Deploy to Azure Container Apps from Docker Hub
# Prerequisites: Azure CLI installed and logged in (az login)

set -e  # Exit on error

# Configuration
DOCKER_USERNAME="franknardelli"
IMAGE_NAME="antenna-tools"
TAG="latest"
RESOURCE_GROUP="antenna-tools-rg"
LOCATION="eastus"
APP_NAME="antenna-tools"
CONTAINER_APP_ENV="antenna-env"

echo "🚀 Deploying to Azure Container Apps..."
echo ""

# Check if logged into Azure
echo "Checking Azure login status..."
az account show > /dev/null 2>&1 || {
    echo "❌ Not logged into Azure. Please run: az login"
    exit 1
}

echo "✅ Azure login confirmed"
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
