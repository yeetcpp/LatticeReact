#!/bin/bash
# LatticeReAct Demo Script
# Shows all the different ways to interact with the system

set -e

echo "🎬 LatticeReAct Demo Script"
echo "=========================="
echo ""

# Check if system is ready
echo "1️⃣ Checking System Status..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker not running"
    exit 1
fi

if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "❌ Ollama not running"
    echo "   Start with: ollama serve"
    exit 1
fi

if ! docker images -q latticereact-app | grep -q .; then
    echo "📦 Building Docker image..."
    docker build -t latticereact-app .
fi

echo "✅ System ready!"
echo ""

echo "2️⃣ Demo: Quick Query Tool"
echo "-------------------------"
echo "Testing with: 'What is the formation energy of NaCl?'"
echo ""
python3 quick-query.py "What is the formation energy of NaCl?"
echo ""

echo "3️⃣ Demo: Raw Docker Command"
echo "----------------------------"
echo "Testing with direct Docker execution..."
echo ""
timeout 60 docker run --rm --env-file .env --network=host latticereact-app \
    python run_supervisor.py --quiet "What are the properties of Silicon?" || echo "Query completed"
echo ""

echo "4️⃣ Interactive Chat Interface Available"
echo "---------------------------------------"
echo "To start the full interactive chat:"
echo "  ./start-chat.sh"
echo ""
echo "Chat features:"
echo "  🎯 Natural language queries"
echo "  💬 Multi-turn conversations"
echo "  📊 Real-time processing indicators"
echo "  💾 Session history and saving"
echo "  🛠️  Built-in help and commands"
echo ""

echo "5️⃣ Available Interaction Methods"
echo "--------------------------------"
echo "Method 1: Interactive Chat (Recommended)"
echo "  ./start-chat.sh"
echo ""
echo "Method 2: Quick Queries"
echo "  python3 quick-query.py \"Your question\""
echo ""
echo "Method 3: Direct Docker"
echo "  docker run --rm --env-file .env --network=host latticereact-app python run_supervisor.py --quiet \"Question\""
echo ""
echo "Method 4: Background Container"
echo "  docker run -d --name lr --env-file .env --network=host latticereact-app tail -f /dev/null"
echo "  docker exec lr python run_supervisor.py --quiet \"Question\""
echo "  docker rm -f lr  # cleanup"
echo ""

echo "🎉 Demo Complete!"
echo ""
echo "Ready for hackathon demo! Start with: ./start-chat.sh"