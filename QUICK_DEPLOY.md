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
