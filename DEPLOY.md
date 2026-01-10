# Azure Container Apps Deployment Guide

This guide covers deploying your Streamlit Antenna Tools to Azure Container Apps.

## Prerequisites

1. **Azure Account**: Free tier available at https://azure.microsoft.com/free
2. **Azure CLI**: Install from https://docs.microsoft.com/cli/azure/install-azure-cli
3. **Docker** (optional for local testing): https://www.docker.com/get-started

## Quick Start

### Option 1: Deploy from Local Machine

```bash
# 1. Login to Azure
az login

# 2. Set variables (customize these)
RESOURCE_GROUP="antenna-tools-rg"
LOCATION="eastus"
APP_NAME="antenna-tools-app"
CONTAINER_APP_ENV="antenna-tools-env"
DOCKER_USER="franknardelli"  # Your Docker Hub username

# 3. Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 4. Create Container Apps environment
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# 5. Deploy container app (Using Public Docker Hub)
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image docker.io/$DOCKER_USER/antenna-tools:latest \
  --target-port 8501 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 2

# 6. Get the app URL
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

Your app will be available at: `https://<app-name>.<random>.azurecontainerapps.io`

### Option 2: Test Locally First

```bash
# Build the Docker image
docker build -t antenna-tools:local .

# Run locally
docker run -p 8501:8501 antenna-tools:local

# Open browser to http://localhost:8501
```

## Updating Your App

Simply run the deployment script again. It handles building, pushing, and updating Azure:

```bash
./deploy-to-azure.sh
```

## For Your IT Department

If your IT department needs to deploy this on corporate Azure:

1. **Provide them with**:
   - This repository or ZIP file
   - This DEPLOY.md file
   - The Dockerfile

2. **They should**:
   - Review the Dockerfile for security compliance
   - Deploy to their Azure subscription using the commands above
   - Configure any required network policies or private endpoints
   - Set up Azure AD authentication if needed

3. **Network Configuration** (if needed):
   ```bash
   # Make app accessible only from corporate network
   az containerapp ingress update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --type internal
   ```

## Cost Optimization

Azure Container Apps free tier includes:
- 180,000 vCPU-seconds per month
- 360,000 GiB-seconds per month
- 2 million requests per month

To stay within free tier:
- Set `--min-replicas 0` (app scales to zero when idle)
- Use `--cpu 0.5 --memory 1.0Gi` (smaller resource allocation)

## Monitoring

```bash
# View logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Check app status
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.runningStatus
```

## Troubleshooting

### App won't start
```bash
# Check logs for errors
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --tail 50

# Check revision status
az containerapp revision list --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### Can't access app
```bash
# Verify ingress is external
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.external
```

### Out of memory
```bash
# Increase memory allocation
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --memory 2.0Gi
```

## Cleanup

```bash
# Delete everything (stops all charges)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Security Notes

1. **HTTPS**: Automatically enabled by Azure Container Apps
2. **Secrets**: Store sensitive data in Azure Key Vault and reference in container app
3. **Authentication**: Can enable Azure AD auth:
   ```bash
   az containerapp auth update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --unauthenticated-client-action RedirectToLoginPage \
     --redirect-provider azureactivedirectory
   ```

## Alternative: Deploy with Docker Hub

If you prefer Docker Hub instead of ACR:

```bash
# Build and push to Docker Hub
docker build -t yourusername/antenna-tools:latest .
docker push yourusername/antenna-tools:latest

# Deploy without registry credentials (for public images)
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image yourusername/antenna-tools:latest \
  --target-port 8501 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 2
```

## Support

- Azure Container Apps docs: https://docs.microsoft.com/azure/container-apps/
- Streamlit docs: https://docs.streamlit.io/
- Azure free account: https://azure.microsoft.com/free/
