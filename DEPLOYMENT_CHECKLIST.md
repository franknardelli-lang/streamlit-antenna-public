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
export APP_NAME="antenna-tools"
export CONTAINER_APP_ENV="antenna-env"
export DOCKER_USER="franknardelli"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Container Apps environment
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 2: Build and Deploy

Run the unified deployment script:

```bash
./deploy-to-azure.sh
```

### Step 3: Access Your App

Your app will be available at:
```
https://<app-name>.<random-id>.<region>.azurecontainerapps.io
```

## 🔄 Update Your App

When you make changes:

```bash
./deploy-to-azure.sh
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
