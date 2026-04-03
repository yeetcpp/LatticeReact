"""ChromaDB cache for LatticeReAct - stores and retrieves query results."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

import hashlib
import json
from pathlib import Path
from typing import Optional

try:
    import chromadb
except ImportError:
    chromadb = None

from config import CHROMA_PERSIST_PATH, SIMILARITY_THRESHOLD


class MaterialsCache:
    """ChromaDB-based cache for materials science query results."""
    
    def __init__(self, persist_path: str = CHROMA_PERSIST_PATH):
        """
        Initialize ChromaDB cache.
        
        Args:
            persist_path: Path to ChromaDB persistent storage
        """
        if chromadb is None:
            raise ImportError("chromadb library not installed. Run: pip install chromadb")
        
        # Create persist directory if needed
        Path(persist_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_path)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="materials_queries",
            metadata={"hnsw:space": "cosine"}
        )
    
    def _hash_query(self, query: str) -> str:
        """Generate deterministic hash for query."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def check_cache(self, query: str) -> Optional[str]:
        """
        Check if query result exists in cache.
        
        Args:
            query: Materials science query string
            
        Returns:
            Cached result if found, None otherwise
        """
        try:
            query_hash = self._hash_query(query)
            
            # Search for similar queries
            results = self.collection.query(
                query_texts=[query],
                n_results=1,
                where={"query_hash": query_hash}
            )
            
            if results and results["ids"] and len(results["ids"]) > 0:
                # Check similarity threshold
                distances = results.get("distances", [[]])[0]
                if distances and (1 - distances[0]) >= SIMILARITY_THRESHOLD:
                    # Exact match found, return cached result
                    metadatas = results.get("metadatas", [[]])[0]
                    if metadatas and len(metadatas) > 0:
                        return metadatas[0].get("result")
            
            return None
        except Exception as e:
            print(f"Cache check error: {str(e)}")
            return None
    
    def store_cache(self, query: str, result: str) -> bool:
        """
        Store query result in cache.
        
        Args:
            query: Materials science query string
            result: Query result/answer
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            query_hash = self._hash_query(query)
            doc_id = f"doc_{query_hash}"
            
            # Store in ChromaDB
            self.collection.add(
                ids=[doc_id],
                documents=[query],
                metadatas=[{
                    "query_hash": query_hash,
                    "result": result,
                    "query": query
                }]
            )
            
            return True
        except Exception as e:
            print(f"Cache store error: {str(e)}")
            return False
    
    def clear_cache(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            # Delete and recreate collection
            self.client.delete_collection(name="materials_queries")
            self.collection = self.client.get_or_create_collection(
                name="materials_queries",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Cache clear error: {str(e)}")
            return False
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        try:
            count = self.collection.count()
            return {"cached_queries": count, "status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # Test cache functionality
    cache = MaterialsCache()
    
    print("Testing ChromaDB Cache...")
    print(f"Cache stats: {cache.get_cache_stats()}")
    
    # Test store and retrieve
    query = "What is the bandgap of GaN?"
    result = "The bandgap of GaN is approximately 3.4 eV at room temperature."
    
    print(f"\nStoring: '{query}'")
    stored = cache.store_cache(query, result)
    print(f"Stored: {stored}")
    
    print(f"\nRetrieving from cache...")
    cached_result = cache.check_cache(query)
    print(f"Cached result: {cached_result}")
    
    print(f"\nFinal cache stats: {cache.get_cache_stats()}")
