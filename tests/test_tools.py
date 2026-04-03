import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

from tools.mp_thermo import search_mp_thermo
from tools.mp_elastic import search_mp_elastic
from tools.mp_electronic import search_mp_electronic


def test_tool(name: str, tool_func, query: str) -> bool:
    """
    Test a single tool and return True if it passes, False otherwise.
    
    Asserts:
    - Result does not start with "API Error"
    - Result contains at least 50 characters
    """
    print(f"\nTest: {name}")
    print(f"Query: {query}")
    
    try:
        # LangChain tools are StructuredTool objects, call using .invoke()
        result = tool_func.invoke({"query": query})
        
        # Check for API errors
        if result.startswith("API Error"):
            print(f"FAIL - API Error returned: {result[:100]}")
            return False
        
        # Check minimum length
        if len(result) < 50:
            print(f"FAIL - Result too short ({len(result)} chars): {result}")
            return False
        
        # All checks passed
        print(f"PASS - Result length: {len(result)} chars")
        print(f"Result preview: {result[:150]}...")
        return True
        
    except Exception as e:
        print(f"FAIL - Exception raised: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Run all tool tests."""
    print("="*80)
    print("LatticeReAct Tool Tests")
    print("="*80)
    
    tests = [
        ("Thermo Tool", search_mp_thermo, "formation energy of Fe2O3"),
        ("Elastic Tool", search_mp_elastic, "bulk modulus of Cu"),
        ("Electronic Tool", search_mp_electronic, "bandgap of SiO2"),
    ]
    
    results = []
    for name, tool_func, query in tests:
        passed = test_tool(name, tool_func, query)
        results.append((name, passed))
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} passed")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
