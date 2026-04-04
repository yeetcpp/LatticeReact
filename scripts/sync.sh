#!/bin/bash
set -e

echo "🔄 Syncing from SSH development environment"
echo "=========================================="

# Detect Docker Compose command (v1 vs v2)
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker compose"  # Default for modern Docker
fi

# Configuration
SSH_HOST=${1:-"your-ssh-host"}
SSH_USER=${2:-"your-username"}
PROJECT_PATH=${3:-"~/Documents/TempFileRith/LatticeReAct"}
LOCAL_PATH=${4:-"."}

if [ "$SSH_HOST" = "your-ssh-host" ]; then
    echo "Usage: $0 <ssh-host> <ssh-user> [remote-path] [local-path]"
    echo ""
    echo "Example:"
    echo "  $0 your-server.com username ~/Documents/TempFileRith/LatticeReAct ."
    echo ""
    echo "This script will:"
    echo "  1. Pull latest changes from git remote"
    echo "  2. Rsync code changes from SSH server"
    echo "  3. Restart Docker services if needed"
    exit 1
fi

# Sync via git (recommended)
echo "📦 Pulling latest changes via git..."
git pull origin main || echo "⚠️  Git pull failed or no remote configured"

# Alternative: Direct rsync sync
echo "🔄 Syncing additional changes via rsync..."
rsync -avz --exclude-from=.dockerignore \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='cache/' \
    --exclude='logs/' \
    "${SSH_USER}@${SSH_HOST}:${PROJECT_PATH}/" \
    "${LOCAL_PATH}/"

echo "✅ Sync complete!"

# Check if services need restart
if $COMPOSE_CMD ps | grep -q "latticereact"; then
    echo "🐳 Restarting Docker services..."
    $COMPOSE_CMD down
    $COMPOSE_CMD up -d
    echo "✅ Services restarted"
else
    echo "ℹ️  Services not running, use ./scripts/setup.sh to start"
fi

echo ""
echo "🎯 Ready for testing! Run ./scripts/test.sh to verify everything works."