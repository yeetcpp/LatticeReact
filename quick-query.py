#!/usr/bin/env python3
"""
Quick Materials Query Tool
=========================
One-off query tool for when you just want to ask one question quickly.
"""

import sys
import subprocess
import time

def quick_query(question):
    """Run a single query and return the result"""
    print(f"🔬 Querying: {question}")
    print("🧪 Processing...")
    
    # Start container if needed
    container_name = "latticereact-quick"
    
    # Clean up any existing container
    subprocess.run(["docker", "rm", "-f", container_name], 
                  capture_output=True)
    
    # Run query in one-shot container
    cmd = [
        "docker", "run", "--rm", "--name", container_name,
        "--env-file", ".env", "--network=host",
        "latticereact-app", 
        "python", "run_supervisor.py", "--quiet", question
    ]
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"\n{'='*60}")
            print("🤖 LatticeReAct Response:")
            print(f"{'='*60}")
            print(result.stdout)
            print(f"⏱️  Completed in {end_time - start_time:.1f}s")
        else:
            print(f"❌ Query failed: {result.stderr}")
            return 1
            
    except subprocess.TimeoutExpired:
        print("⏱️ Query timeout (3 minutes)")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Query interrupted")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quick-query.py \"Your materials question\"")
        print("\nExamples:")
        print("  python3 quick-query.py \"What is the bandgap of Silicon?\"")
        print("  python3 quick-query.py \"What are the elastic properties of Iron?\"")
        return 1
        
    question = " ".join(sys.argv[1:])
    return quick_query(question)

if __name__ == "__main__":
    sys.exit(main())