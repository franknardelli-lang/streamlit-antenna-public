#!/bin/bash

# Configuration
SERVER_USER="alan"
SERVER_IP="192.168.1.162"
APP_FOLDER="~/apps/streamlit-antenna-public"

echo "🚀 Pushing changes to GitHub..."
git push

echo "🔄 Updating XPS Server..."

# 1. Remove '-t' (it kills background jobs)
# 2. Use '|| true' after pkill so script doesn't stop if no app is running
# 3. Use direct path './venv/bin/python' instead of activating
ssh $SERVER_USER@$SERVER_IP "cd $APP_FOLDER && \
git pull && \
./venv/bin/pip install -r requirements.txt && \
pkill -f streamlit || true; \
nohup ./venv/bin/python -m streamlit run Home.py --server.port 8501 --server.address 0.0.0.0 > app.log 2>&1 & exit"

echo "✅ Deployed! App is running at http://$SERVER_IP:8501"