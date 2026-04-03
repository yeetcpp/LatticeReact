"""Test script for LatticeReAct FastAPI backend."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*80)
    print("Testing /health endpoint")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_query(query: str):
    """Test query endpoint."""
    print("\n" + "="*80)
    print(f"Testing /query endpoint with: {query}")
    print("="*80)
    
    try:
        payload = {"query": query}
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            timeout=120
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Source: {result['source']}")
            print(f"Disclaimer: {result['disclaimer'][:100]}...")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_cache_stats():
    """Test cache stats endpoint."""
    print("\n" + "="*80)
    print("Testing /cache/stats endpoint")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/cache/stats", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test health
    test_health()
    
    # Test cache stats
    test_cache_stats()
    
    # Test simple query
    test_query("bandgap of GaN")
    
    # Test cache hit
    test_query("bandgap of GaN")
    
    # Test cache stats again
    test_cache_stats()
    
    print("\n" + "="*80)
    print("Testing complete!")
    print("="*80)
