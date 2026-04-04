#!/bin/bash
set -e

echo "🚀 Setting up LatticeReAct Docker Environment"
echo "============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🔧 Using Docker with host networking (for existing Ollama)"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env file and add your MP_API_KEY before proceeding"
    echo "   You can get an API key from: https://materialsproject.org/api"
    read -p "Press Enter when you've added your API key to .env..."
fi

# Source .env file to check MP_API_KEY
set -a
source .env
set +a

if [ -z "$MP_API_KEY" ] || [ "$MP_API_KEY" = "your_mp_api_key_here" ]; then
    echo "❌ MP_API_KEY not set in .env file. Please add your Materials Project API key."
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "❌ Ollama not running on localhost:11434"
    echo "   Please start Ollama first: ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# Check if required model exists
if ! curl -s http://localhost:11434/api/tags | grep -q "qwen2.5:14b-instruct-q8_0"; then
    echo "📥 Pulling required model..."
    ollama pull qwen2.5:14b-instruct-q8_0
fi

echo "🐳 Building LatticeReAct Docker image..."
docker build -t latticereact-app .

echo ""
echo "✅ LatticeReAct Docker setup complete!"
echo ""
echo "🧪 Test the system:"
echo "   ./scripts/test.sh"
echo ""
echo "🔬 Run a query:"
echo "   docker run --rm --env-file .env --network=host latticereact-app python run_supervisor.py --quiet \"What is the bulk modulus of Iron?\""
echo ""
echo "🖥️ Interactive mode:"
echo "   docker run -it --env-file .env --network=host latticereact-app /bin/bash"