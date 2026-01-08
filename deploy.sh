#!/bin/bash

# Configuration
SERVER_USER="alan"
SERVER_IP="192.168.1.162"
APP_FOLDER="~/apps/streamlit-antenna-public"

echo "🚀 Pushing changes to GitHub..."
git push

echo "🔄 Updating XPS Server..."
# 1. Pull code
# 2. Run the script we just made
ssh $SERVER_USER@$SERVER_IP "cd $APP_FOLDER && git pull && ./run.sh"

echo "✅ Deployed! App is running at http://$SERVER_IP:8501"