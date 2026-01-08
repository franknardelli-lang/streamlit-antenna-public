#!/bin/bash

# Configuration
SERVER_USER="alan"
SERVER_IP="192.168.1.162"
APP_FOLDER="~/apps/streamlit-antenna-public"

echo "🚀 Pushing changes to GitHub..."
git push

echo "🔄 Updating XPS Server..."
ssh -t $SERVER_USER@$SERVER_IP "cd $APP_FOLDER && \
git pull && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
pkill -f streamlit; \
nohup python3 -m streamlit run Home.py --server.port 8501 --server.address 0.0.0.0 > app.log 2>&1 &"

echo "✅ Deployed! App is running at http://$SERVER_IP:8501"