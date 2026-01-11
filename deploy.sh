#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# Configuration
SERVER_USER="alan"
SERVER_IP="192.168.1.162"
APP_FOLDER="/opt/stacks/streamlit-antenna-public"

echo "🚀 Pushing changes to GitHub..."
git push

echo "🔄 Deploying to Linux Server ($SERVER_IP) using Docker..."

# Define the sequence of commands to be executed on the remote server.
# Using a multi-line string makes it easier to read and maintain.
REMOTE_COMMANDS=$(cat <<EOF
set -e # Ensure remote script also exits on error

echo "[REMOTE] Changing to app directory: $APP_FOLDER"
cd $APP_FOLDER

echo "[REMOTE] Pulling latest code from GitHub..."
git pull

echo "[REMOTE] Stopping and removing old container (if exists)..."
docker stop antenna-tools-container || true
docker rm antenna-tools-container || true

echo "[REMOTE] Building and starting container with Docker Compose..."
docker compose up -d --build
EOF
)

# Execute the commands on the remote server via SSH
ssh $SERVER_USER@$SERVER_IP "bash -c '$REMOTE_COMMANDS'"

echo "✅ Deployment complete! App should be running at http://$SERVER_IP:8501"