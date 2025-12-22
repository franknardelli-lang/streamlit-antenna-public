# Quick Deployment Guide

## 🚀 Deploy Your Streamlit Apps to Azure

You have everything set up! Here's how to deploy:

### Step 1: Build and Push to Docker Hub (On your local machine)

Since you're SSH'd into your local machine with Docker Desktop:

```bash
cd /workspaces/streamlit-antenna-public

# Build and push to Docker Hub
./build-and-push.sh
```

**What this does:**
- Builds your Docker image locally
- Asks you to login to Docker Hub (username: `franknardelli`)
- Pushes the image to Docker Hub

**Time:** ~3-5 minutes

### Step 2: Deploy to Azure (From this dev container OR local machine)

After the image is pushed to Docker Hub:

```bash
# Make sure you're logged into Azure
az account show

# If not logged in, run:
# az login

# Deploy to Azure Container Apps
./deploy-to-azure.sh
```

**What this does:**
- Creates Azure Container Apps environment
- Deploys your Streamlit apps from Docker Hub
- Gives you the live URL

**Time:** ~2-3 minutes

---

## 📋 Complete Commands

```bash
# Step 1: On your local machine (where Docker Desktop is)
cd /workspaces/streamlit-antenna-public
./build-and-push.sh

# Step 2: Back in dev container (or local machine)
./deploy-to-azure.sh
```

---

## ✅ What You Already Have

- ✅ Azure account created
- ✅ Azure CLI installed and logged in
- ✅ Resource group created: `antenna-tools-rg`
- ✅ Container Registry created: `antennatools33189`
- ✅ Docker Hub account: `franknardelli`
- ✅ Docker Desktop on local machine

---

## 🎯 Expected Result

After deployment, you'll get a URL like:
```
https://antenna-tools.XXXXX.eastus.azurecontainerapps.io
```

Your apps will be accessible at:
- **Home:** https://your-url/
- **Radiation Pattern Visualizer:** Available in sidebar
- **CSV Processor:** Available in sidebar

---

## 🔄 Updating an Existing Deployment

Already deployed and need to update with new changes? Follow these steps:

### Step 1: Build and Push Updated Image (Local Machine)

From your **local machine** terminal (where Docker Desktop is running):

```bash
cd ~/github/streamlit-antenna-public
./build-and-push.sh
```

**What this does:**
- Rebuilds your Docker image with the latest code changes
- Pushes the new image to Docker Hub with the `:latest` tag

**Time:** ~3-5 minutes

### Step 2: Update Azure Deployment (Dev Container)

From your **dev container** terminal (where Azure CLI is logged in):

```bash
./deploy-to-azure.sh
```

**What this does:**
- Detects that the app already exists
- Runs `az containerapp update` instead of create
- Pulls the new `:latest` image from Docker Hub
- Updates the running container app
- No downtime needed - Azure handles the rollout

**Time:** ~1-2 minutes

### Quick Reference

| Step | Where to Run | Command |
|------|--------------|---------|
| 1. Build & Push | Local Machine (Docker Desktop) | `./build-and-push.sh` |
| 2. Update Azure | Dev Container (Azure CLI) | `./deploy-to-azure.sh` |

**Your Live URL:** https://antenna-tools.greenstone-d56397b4.eastus.azurecontainerapps.io/

### Force Update (If deploy-to-azure.sh doesn't pull new image)

Sometimes Azure caches the `:latest` tag and doesn't pull the new image. Use this command to force an update:

```bash
az containerapp update \
  --name antenna-tools \
  --resource-group antenna-tools-rg \
  --image docker.io/franknardelli/antenna-tools:latest \
  --revision-suffix $(date +%s)
```

**What the revision suffix does:**
- Creates a new revision with a timestamp (e.g., `antenna-tools--1766363310`)
- Forces Azure to pull the latest image from Docker Hub
- Routes 100% traffic to the new revision automatically
- Old revision is kept but set to 0% traffic (automatic rollback available if needed)

---

## 📊 Monitoring Deployment Status

### Check Active Revisions

See all revisions and their traffic distribution:

```bash
az containerapp revision list \
  --name antenna-tools \
  --resource-group antenna-tools-rg \
  --output table
```

**Output example:**
```
CreatedTime                Active    Replicas    TrafficWeight    HealthState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------------
2025-12-22T00:21:21+00:00  True      1           0                Healthy        antenna-tools--1766362871
2025-12-22T00:28:40+00:00  True      1           100              Healthy        antenna-tools--1766363310
```

**What to look for:**
- **TrafficWeight**: 100 means this revision is live and receiving all traffic
- **HealthState**: "Healthy" means container is running properly
  - "None" means container is still starting up (wait 30-60 seconds)
  - "Unhealthy" means something is wrong (check logs)
- **Active**: True means the revision is still deployed

### Check Current Image

Verify which Docker image is currently deployed:

```bash
az containerapp show \
  --name antenna-tools \
  --resource-group antenna-tools-rg \
  --query "properties.template.containers[0].image" \
  --output tsv
```

### View Logs (If Troubleshooting)

If something isn't working, check the container logs:

```bash
az containerapp logs show \
  --name antenna-tools \
  --resource-group antenna-tools-rg \
  --follow
```

Press `Ctrl+C` to exit log viewing.

### Typical Update Timeline

1. **0:00** - Run force update command
2. **0:30** - New revision created (HealthState: None)
3. **1:00** - Container starting (HealthState: None)
4. **1:30** - Container healthy (HealthState: Healthy)
5. **2:00** - Full rollout complete, old revision at 0% traffic

**Total time:** ~1-2 minutes for simple updates

---

## 🆘 Troubleshooting

**Build fails?**
- Make sure Docker Desktop is running
- Check you're in the project directory

**Push fails?**
- Login to Docker Hub: `docker login`
- Username: `franknardelli`

**Deploy fails?**
- Make sure Azure CLI is logged in: `az login`
- Check resource group exists: `az group show --name antenna-tools-rg`

---

## 💰 Cost

With your current configuration:
- **Free tier covers:** 180,000 vCPU-seconds/month
- **Your usage:** ~0.5 vCPU
- **Scales to zero:** When idle = $0
- **Expected cost:** $0/month for personal use

---

Ready to deploy? Run `./build-and-push.sh` on your local machine!
