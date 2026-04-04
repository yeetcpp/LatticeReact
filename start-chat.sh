#!/bin/bash
# LatticeReAct Chat Launcher
# Quick launcher script for the interactive chat interface

set -e

echo "🚀 Starting LatticeReAct Interactive Chat"
echo "========================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "chat.py" ]; then
    echo "❌ chat.py not found. Please run from LatticeReAct directory."
    exit 1
fi

# Install required Python packages if needed
echo "📦 Checking Python dependencies..."
python3 -c "import requests" 2>/dev/null || {
    echo "Installing requests package..."
    pip3 install requests || {
        echo "❌ Failed to install requests. Please install manually: pip3 install requests"
        exit 1
    }
}

# Launch the chat interface
echo "🎯 Launching chat interface..."
echo ""
python3 chat.py