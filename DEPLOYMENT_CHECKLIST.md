# Deployment Checklist

## ✅ Pre-Deployment Validation

- [x] All files created and validated
- [x] Python imports working correctly
- [x] Multi-page app structure configured
- [x] Streamlit config optimized for production
- [x] Dockerfile created with health checks
- [x] .dockerignore configured to reduce image size

## 🧪 Test Locally (Optional but Recommended)

```bash
# Option 1: Test with Streamlit directly
streamlit run Home.py

# Option 2: Test with Docker (if you have Docker installed)
docker build -t antenna-tools:test .
docker run -p 8501:8501 antenna-tools:test
# Then open http://localhost:8501
```

## 🚀 Deploy to Azure Container Apps

### Step 1: Setup Azure (One-time)

```bash
# Login
az login

# Set your variables (customize these!)
export RESOURCE_GROUP="antenna-tools-rg"
export LOCATION="eastus"
export ACR_NAME="antennatoolsacr"  # Must be unique, lowercase, alphanumeric
export APP_NAME="antenna-tools"
export CONTAINER_APP_ENV="antenna-env"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Create Container Apps environment
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 2: Build and Deploy

```bash
# Build in Azure (no local Docker needed!)
az acr build \
  --registry $ACR_NAME \
  --image antenna-tools:latest \
  --file Dockerfile \
  .

# Get ACR credentials
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Deploy the app
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $ACR_SERVER/antenna-tools:latest \
  --registry-server $ACR_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8501 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 2

# Get your app URL
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

### Step 3: Access Your App

Your app will be available at:
```
https://<app-name>.<random-id>.<region>.azurecontainerapps.io
```

## 🔄 Update Your App

When you make changes:

```bash
# Rebuild image
az acr build \
  --registry $ACR_NAME \
  --image antenna-tools:latest \
  --file Dockerfile \
  .

# Update app (pulls new image automatically)
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

## 📊 Monitor Your App

```bash
# View logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Check status
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.runningStatus
```

## 🏢 For IT Department Deployment

Share these files with IT:
1. Entire repository or ZIP file
2. [DEPLOY.md](DEPLOY.md) - Detailed deployment guide
3. This checklist
4. [Dockerfile](Dockerfile) - For security review

They can deploy to corporate Azure using the same commands above.

### Network Isolation (if required)

```bash
# Make app internal-only (accessible via VPN/private network)
az containerapp ingress update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --type internal
```

## 💰 Cost Optimization

Current configuration uses:
- `--min-replicas 0` - Scales to zero when idle (saves money!)
- `--cpu 0.5 --memory 1.0Gi` - Minimal resources
- **Free tier covers**: 180,000 vCPU-seconds/month, 360,000 GiB-seconds/month

**Expected cost for light usage**: $0/month (within free tier)

## 🧹 Cleanup

To delete everything and stop all charges:

```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## 📚 Additional Resources

- [Full Deployment Guide](DEPLOY.md)
- [Azure Container Apps Docs](https://docs.microsoft.com/azure/container-apps/)
- [Streamlit Docs](https://docs.streamlit.io/)
