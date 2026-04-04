#!/bin/bash
# Quick development helper for Mac users

echo "🍎 LatticeReAct Mac Development Setup"
echo "===================================="

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop for Mac"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install git"
    exit 1
fi

echo "✅ Dependencies check passed"

# Get project path
PROJECT_PATH=$(pwd)
echo "📁 Working in: $PROJECT_PATH"

# Setup environment
if [ ! -f .env ]; then
    cp .env.template .env
    echo "📝 Created .env file. Please add your MP_API_KEY:"
    echo "   1. Get API key from: https://materialsproject.org/api"
    echo "   2. Edit .env file and replace 'your_mp_api_key_here' with your actual key"
    read -p "Press Enter when ready..."
fi

# Run setup
echo "🚀 Starting Docker setup..."
./scripts/setup.sh

echo ""
echo "🎉 Setup complete! Your LatticeReAct system is running."
echo ""
echo "💡 Next steps:"
echo "   • Test: ./scripts/test.sh"
echo "   • Query: docker-compose exec app python run_supervisor.py --quiet \"Your question\""
echo "   • Logs: docker-compose logs -f app"
echo "   • Sync from SSH: ./scripts/sync.sh your-server username"
echo ""
echo "🔗 Access points:"
echo "   • Ollama API: http://localhost:11434"
echo "   • Backend: http://localhost:8000"  
echo "   • Frontend: http://localhost:3000 (when ready)"