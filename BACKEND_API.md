# LatticeReAct FastAPI Backend

## Overview

The FastAPI backend provides a REST API interface for the LatticeReAct hierarchical agent system. It includes query processing with caching, health checks, and cache management endpoints.

## Features

✅ **Query Processing**: POST `/query` endpoint for materials science questions
✅ **Caching**: ChromaDB-based caching for query results and performance
✅ **Health Check**: `/health` endpoint for service monitoring
✅ **Cache Management**: `GET /cache/stats` and `POST /cache/clear` endpoints
✅ **CORS Support**: Cross-origin requests enabled
✅ **Error Handling**: Comprehensive error handling with detailed messages

## Installation

```bash
pip install fastapi pydantic uvicorn chromadb langchain langchain-ollama
```

## Running the Server

```bash
# Direct execution
python3 backend/main.py

# Or with uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Endpoints

### 1. Health Check
- **Endpoint**: `GET /health`
- **Response**: `{"status": "running"}`

```bash
curl http://localhost:8000/health
```

### 2. Query Materials
- **Endpoint**: `POST /query`
- **Request**:
  ```json
  {
    "query": "What is the bandgap of GaN?"
  }
  ```
- **Response**:
  ```json
  {
    "answer": "The bandgap of GaN is approximately...",
    "source": "live",
    "disclaimer": "This data is retrieved from the Materials Project database..."
  }
  ```

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "bandgap of GaN"}'
```

### 3. Cache Statistics
- **Endpoint**: `GET /cache/stats`
- **Response**: `{"cached_queries": 5, "status": "ok"}`

```bash
curl http://localhost:8000/cache/stats
```

### 4. Clear Cache
- **Endpoint**: `POST /cache/clear`
- **Response**: `{"status": "cleared"}`

```bash
curl -X POST http://localhost:8000/cache/clear
```

## Architecture

```
FastAPI Application
├── Health Check Endpoint
├── Query Processing Pipeline
│   ├── Check Cache (ChromaDB)
│   ├── If Cache Miss:
│   │   ├── Call Supervisor Agent
│   │   ├── Wait for Result
│   │   └── Store in Cache
│   └── Return QueryResponse
└── Cache Management Endpoints
```

## Query Processing Flow

1. **Request**: Client sends query via POST `/query`
2. **Validation**: Query string is validated (not empty)
3. **Cache Check**: Query is checked against ChromaDB cache
   - **Cache Hit**: Return cached result with `source="cache"`
   - **Cache Miss**: Continue to step 4
4. **Supervisor Invocation**: LatticeReAct supervisor processes query
5. **Result Storage**: Successful result stored in cache
6. **Response**: Return result with `source="live"`

## Classes

### QueryRequest
Pydantic model for query requests.

```python
class QueryRequest(BaseModel):
    query: str
```

### QueryResponse
Pydantic model for query responses.

```python
class QueryResponse(BaseModel):
    answer: str
    source: str  # "cache" or "live"
    disclaimer: str
```

## Error Handling

- **400 Bad Request**: Empty query
- **500 Internal Server Error**: Processing errors with detailed messages
- All errors include descriptive detail messages

## Environment Variables

The application uses variables from `config.py`:
- `CHROMA_PERSIST_PATH`: Path to ChromaDB storage (default: `./cache/chromadb`)
- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `MODEL_NAME`: Ollama model name (default: `qwen2.5:14b-instruct-q8_0`)
- `MP_API_KEY`: Materials Project API key (from `.env`)

## Testing

Use the provided test script:

```bash
# Start backend in background
python3 backend/main.py &

# Run tests in another terminal
python3 backend/test_api.py
```

## Example Queries

Some example materials science queries that work well:

```bash
# Thermodynamic queries
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "formation energy of GaN"}'

# Elastic property queries
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "bulk modulus of Iron"}'

# Electronic structure queries
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "bandgap of GaN"}'

# Complex multi-tool queries
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the stiffest material with the lowest formation energy in the Si-O system?"}'
```

## Performance Notes

- First query for a material will take 30-60 seconds (via supervisor agent)
- Subsequent identical queries return instantly from cache
- Cache is persistent across server restarts (stored in ChromaDB)
- Maximum iteration limit: 5 per query
