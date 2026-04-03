# LatticeReAct Setup Guide

Complete guide to starting the LatticeReAct hierarchical agent system with frontend and backend.

## Prerequisites

- Python 3.9+
- Ollama running with `qwen2.5:14b-instruct-q8_0` model
- Materials Project API key (set in `.env` file)

## Environment Setup

### 1. Create `.env` file

In the root of the LatticeReAct directory, create a `.env` file with your Materials Project API key:

```bash
cat > .env << 'EOF'
MP_API_KEY=your_materials_project_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=qwen2.5:14b-instruct-q8_0
CHROMA_PERSIST_PATH=./cache/chromadb
SIMILARITY_THRESHOLD=0.2
EOF
```

Replace `your_materials_project_api_key_here` with your actual Materials Project API key.

### 2. Create Virtual Environment

```bash
cd /home/letushack/Documents/TempFileRith/LatticeReAct
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR on Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install fastapi pydantic uvicorn chromadb langchain langchain-community langchain-ollama requests python-dotenv streamlit
```

## Running the System

### Terminal 1: FastAPI Backend

```bash
cd /home/letushack/Documents/TempFileRith/LatticeReAct
source venv/bin/activate  # If not already activated

# Run the backend
python3 backend/main.py
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

The backend will be available at `http://localhost:8000`

**Health Check:**
```bash
curl http://localhost:8000/health
```

### Terminal 2: Streamlit Frontend

```bash
cd /home/letushack/Documents/TempFileRith/LatticeReAct
source venv/bin/activate  # If not already activated

# Run the frontend
streamlit run frontend/app.py
```

You should see output like:
```
You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

The frontend will be available at `http://localhost:8501`

## Using LatticeReAct

### Via Web UI (Recommended)

1. Open `http://localhost:8501` in your browser
2. Use the **Quick Examples** buttons or enter a custom query
3. Click **Submit Query** to get an answer
4. Results show:
   - The AI-generated answer
   - Source: "Cache" (instant) or "Live API" (newly computed)
   - Disclaimer about data accuracy

### Example Queries

Try these queries to test the system:

**Single-Tool Queries:**
- "Bulk modulus of Iron" (elastic properties)
- "Bandgap of GaN" (electronic structure)
- "Formation energy of Si" (thermodynamics)

**Multi-Tool Queries:**
- "What is the stiffest material with the lowest formation energy in the Si-O system?"
- "Compare the bandgap and bulk modulus of GaN and AlN"

### Via API (for integration)

```bash
# Query the backend directly
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Bandgap of GaN"}'

# Response:
# {
#   "answer": "The bandgap of GaN is...",
#   "source": "live",
#   "disclaimer": "This data is retrieved..."
# }
```

### Cache Management

```bash
# View cache statistics
curl http://localhost:8000/cache/stats
# Response: {"cached_queries": 5, "status": "ok"}

# Clear the cache
curl -X POST http://localhost:8000/cache/clear
# Response: {"status": "cleared"}
```

## System Architecture

```
LatticeReAct System
├── Streamlit Frontend (Port 8501)
│   ├── Query Input Form
│   ├── Example Buttons
│   └── Result Display
│
├── FastAPI Backend (Port 8000)
│   ├── Query Endpoint (/query)
│   ├── Health Check (/health)
│   ├── Cache Management (/cache/*)
│   └── Caching Pipeline
│
├── Supervisor Agent
│   ├── Query Routing
│   ├── Multi-Agent Coordination
│   └── Result Synthesis
│
├── Sub-Agents (3)
│   ├── Thermodynamic Properties Agent
│   ├── Elastic Properties Agent
│   └── Electronic Structure Agent
│
├── Tools (3)
│   ├── search_mp_thermo (Materials Project)
│   ├── search_mp_elastic (Materials Project)
│   └── search_mp_electronic (Materials Project)
│
├── ChromaDB Cache
│   └── Persistent Storage (./cache/chromadb)
│
└── External Dependencies
    ├── Ollama LLM (http://localhost:11434)
    └── Materials Project API (https://api.materialsproject.org)
```

## Performance Notes

- **First Query**: 30-60 seconds (via supervisor agent, LLM reasoning, API calls)
- **Cached Query**: < 1 second (similarity search on ChromaDB)
- **Cache Persistence**: Survives backend restarts (stored in ChromaDB)
- **Max Iterations**: 5 per query (safety limit in supervisor agent)

## Troubleshooting

### Backend fails to start

**Error**: `Cannot connect to Ollama at http://localhost:11434`

**Solution**: 
- Make sure Ollama is running
- Check that the model exists: `ollama list`
- Pull the model if needed: `ollama pull qwen2.5:14b-instruct-q8_0`

### Frontend cannot reach backend

**Error**: `Cannot connect to backend server. Make sure the FastAPI server is running`

**Solution**:
- Verify backend is running: `curl http://localhost:8000/health`
- Check that backend is on port 8000
- Verify no firewall is blocking localhost connections

### API returns N/A values

**Error**: Tools return "N/A" for all fields

**Solution**:
- Check your `.env` file has correct `MP_API_KEY`
- Verify Materials Project API is accessible: `curl https://api.materialsproject.org`
- Try a different material query to verify API connectivity

### Virtual environment not working

**Error**: `command not found: streamlit` or `No module named 'streamlit'`

**Solution**:
```bash
# Verify venv is activated
which python3
# Should show: /home/letushack/Documents/TempFileRith/LatticeReAct/venv/bin/python3

# If not, activate it:
source venv/bin/activate

# Reinstall dependencies:
pip install streamlit requests fastapi uvicorn
```

## Quick Start Script

Create `start.sh` to start both services:

```bash
#!/bin/bash

# Navigate to project directory
cd /home/letushack/Documents/TempFileRith/LatticeReAct

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "Starting FastAPI backend..."
python3 backend/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Streamlit frontend..."
streamlit run frontend/app.py

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
```

Make executable and run:
```bash
chmod +x start.sh
./start.sh
```

## File Structure

```
LatticeReAct/
├── config.py                 # Configuration loading
├── .env                      # Environment variables (create this)
├── venv/                     # Virtual environment (created by setup)
│
├── tools/
│   ├── mp_thermo.py         # Thermodynamic properties tool
│   ├── mp_elastic.py        # Elastic properties tool
│   ├── mp_electronic.py     # Electronic structure tool
│   └── chromadb_cache.py    # Caching system
│
├── agents/
│   ├── thermo_agent.py      # Thermo sub-agent
│   ├── elastic_agent.py     # Elastic sub-agent
│   ├── electronic_agent.py  # Electronic sub-agent
│   └── supervisor.py        # Supervisor agent
│
├── backend/
│   ├── main.py              # FastAPI application
│   └── test_api.py          # API tests
│
├── frontend/
│   └── app.py               # Streamlit application
│
├── tests/
│   └── test_tools.py        # Tool validation tests
│
├── cache/
│   └── chromadb/            # Created on first run
│
├── SETUP.md                 # This file
├── BACKEND_API.md           # Backend documentation
└── README.md                # Project overview
```

## Testing

Run the tool tests:
```bash
source venv/bin/activate
python3 tests/test_tools.py
```

Run the API tests:
```bash
source venv/bin/activate
python3 backend/test_api.py
```

Expected output: All tests should pass with legitimate Materials Project data.

## Support

For issues, check:
1. [BACKEND_API.md](BACKEND_API.md) - Backend API documentation
2. [README.md](README.md) - Project overview
3. Environment variables in `.env`
4. Ollama model availability
