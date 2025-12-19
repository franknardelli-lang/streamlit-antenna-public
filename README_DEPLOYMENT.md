# Antenna Tools - Deployment Quick Start

## What's Included

This deployment package includes:
- 📊 **Link Budget Calculator** - RF link budget calculations with multiple models
- 📈 **CSV Antenna Processor** - Process and combine antenna sweep measurement data

## Deployment Options

### Option 1: Azure Container Apps (Recommended)
Best for: Production deployment with free tier and WebSocket support

See [DEPLOY.md](DEPLOY.md) for complete instructions.

**Quick Deploy:**
```bash
az login
az acr build --registry YOUR_ACR_NAME --image antenna-tools:latest .
az containerapp create --name antenna-tools --image YOUR_ACR.azurecr.io/antenna-tools:latest ...
```

### Option 2: Local Testing
```bash
docker build -t antenna-tools:local .
docker run -p 8501:8501 antenna-tools:local
# Open http://localhost:8501
```

### Option 3: Streamlit Community Cloud
- Push to GitHub
- Connect at https://share.streamlit.io
- Set entrypoint to `Home.py`

## File Structure

```
.
├── Home.py                          # Main landing page
├── pages/                           # Streamlit auto-discovers these
│   ├── 1_📊_Link_Budget_Calculator.py
│   └── 2_📈_CSV_Antenna_Processor.py
├── streamlit_antenna_gui_test.py    # Link budget calculator
├── streamlit_process_all_csv.py     # CSV processor
├── Dockerfile                       # Container build instructions
├── .dockerignore                    # Files to exclude from container
├── .streamlit/config.toml           # Streamlit configuration
├── requirements.txt                 # Python dependencies
└── DEPLOY.md                        # Detailed deployment guide
```

## Running Locally (without Docker)

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## For IT Departments

This is a standard containerized Python application:
- Base image: `python:3.11-slim-bookworm`
- Exposed port: 8501 (HTTP)
- No external database required
- Stateless (scales horizontally)
- HTTPS handled by Azure Container Apps

All dependencies are declared in [requirements.txt](requirements.txt).

## Cost Estimate

**Azure Container Apps Free Tier:**
- 180,000 vCPU-seconds/month (plenty for development)
- 360,000 GiB-seconds/month
- 2M requests/month

With `--min-replicas 0`, the app scales to zero when idle = **$0/month for low usage**

## Support

- Full deployment guide: [DEPLOY.md](DEPLOY.md)
- Azure Container Apps: https://docs.microsoft.com/azure/container-apps/
- Streamlit: https://docs.streamlit.io/
