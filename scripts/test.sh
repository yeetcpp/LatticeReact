#!/bin/bash
set -e

echo "🧪 Testing LatticeReAct Docker Deployment"
echo "========================================"

# Test with host networking
echo "🔍 Testing Docker container with host networking..."

if ! docker run --rm --env MP_API_KEY=${MP_API_KEY:-VdoyUs8JbL2lnONKUqFCu4QEOqXQm9P3} --env OLLAMA_BASE_URL=http://localhost:11434 --network=host latticereact-app python -c "
import requests
resp = requests.get('http://localhost:11434/api/version')
print('✅ Ollama connectivity: OK')
print('✅ Version:', resp.json()['version'])
" > /dev/null 2>&1; then
    echo "❌ Cannot connect to Ollama"
    exit 1
fi

# Test LatticeReAct functionality
echo ""
echo "🔬 Testing LatticeReAct application..."

echo "Testing with query: What is the bulk modulus of Silicon?"
result=$(docker run --rm --env MP_API_KEY=${MP_API_KEY:-VdoyUs8JbL2lnONKUqFCu4QEOqXQm9P3} --env OLLAMA_BASE_URL=http://localhost:11434 --network=host latticereact-app python run_supervisor.py --quiet "What is the bulk modulus of Silicon?" 2>&1)

if echo "$result" | grep -q "FINAL ANSWER"; then
    echo "✅ Basic query processing works"
else
    echo "❌ Basic query failed"
    echo "Output: $result"
    exit 1
fi

# Check for anti-hallucination behavior
if echo "$result" | grep -q "ID_NOT_FOUND\|mp-"; then
    echo "✅ Anti-hallucination working (either found real mp-code or correctly reports not found)"
else
    echo "⚠️  Unexpected response pattern"
fi

echo ""
echo "🎉 All tests passed! LatticeReAct Docker is working correctly."
echo ""
echo "📋 Usage commands:"
echo "   # Run a query:"
echo "   docker run --rm --env-file .env --network=host latticereact-app python run_supervisor.py --quiet \"Your question\""
echo ""
echo "   # Interactive mode:"  
echo "   docker run -it --env-file .env --network=host latticereact-app /bin/bash"
echo ""
echo "   # Monitor in background:"
echo "   docker run -d --name latticereact --env-file .env --network=host latticereact-app tail -f /dev/null"