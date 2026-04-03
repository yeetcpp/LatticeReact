"""FastAPI backend for LatticeReAct - Materials science query service."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

from agents.supervisor import create_supervisor
from tools.chromadb_cache import MaterialsCache


# Initialize FastAPI app
app = FastAPI(
    title="LatticeReAct",
    description="Hierarchical ReAct agent system for materials science queries",
    version="0.1.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache and supervisor globally
cache = MaterialsCache()
supervisor = None


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for materials science queries."""
    query: str


class QueryResponse(BaseModel):
    """Response model for query results."""
    answer: str
    source: str  # "cache" or "live"
    disclaimer: str = "This data is retrieved from the Materials Project database. Results should be verified for production use."


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "running"}


# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_materials(request: QueryRequest):
    """
    Process a materials science query using the supervisor agent.
    
    Checks cache first, then invokes supervisor if needed.
    
    Args:
        request: QueryRequest with query string
        
    Returns:
        QueryResponse with answer, source, and disclaimer
        
    Raises:
        HTTPException: On processing error
    """
    global supervisor
    
    try:
        query = request.query.strip()
        
        if not query:
            raise ValueError("Query cannot be empty")
        
        # Step 1: Check cache
        print(f"\n[API] Checking cache for: {query}")
        cached_result = cache.check_cache(query)
        
        if cached_result:
            print(f"[API] Cache hit! Returning cached result")
            return QueryResponse(
                answer=cached_result,
                source="cache"
            )
        
        # Step 2: Cache miss - create supervisor and invoke
        print(f"[API] Cache miss. Creating supervisor...")
        
        if supervisor is None:
            supervisor = create_supervisor()
        
        print(f"[API] Invoking supervisor with query...")
        result = supervisor.invoke({"input": query})
        
        # Extract answer
        answer = result.get("output", str(result))
        tools_used = result.get("tools_used", [])
        
        print(f"[API] Supervisor completed. Tools used: {tools_used}")
        
        # Step 3: Store in cache
        print(f"[API] Storing result in cache...")
        cache.store_cache(query, answer)
        
        # Step 4: Return response
        return QueryResponse(
            answer=answer,
            source="live"
        )
        
    except ValueError as e:
        print(f"[API] Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        error_traceback = traceback.format_exc()
        
        print(f"[API] Error: {error_msg}")
        print(f"[API] Traceback:\n{error_traceback}")
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


# Cache management endpoints
@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    try:
        stats = cache.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting cache stats: {str(e)}"
        )


@app.post("/cache/clear")
async def clear_cache():
    """Clear the cache."""
    try:
        cleared = cache.clear_cache()
        if cleared:
            return {"status": "cleared"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to clear cache"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("="*80)
    print("Starting LatticeReAct FastAPI Backend")
    print("="*80)
    print("\nServer running at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("Cache stats at: http://localhost:8000/cache/stats")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
