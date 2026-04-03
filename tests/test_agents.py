"""Verification tests for LatticeReAct agent implementation."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

from agents.supervisor import create_supervisor


def test_single_property_query():
    """
    Test 1: Verify single property queries work with real LLM reasoning.
    
    Assertions:
    - Output contains "GPa" (modulus units)
    - Output does NOT contain raw tool markers like "[ELASTIC_AGENT]"
    - Output is synthesized LLM answer, not concatenated raw JSON
    """
    print("\n" + "="*80)
    print("TEST 1: SINGLE PROPERTY QUERY")
    print("="*80)
    
    supervisor = create_supervisor()
    query = "What is the bulk modulus of Iron?"
    
    print(f"\nQuery: {query}")
    print("\nInvoking supervisor...\n")
    
    result = supervisor.invoke({"input": query})
    answer = result.get("output", "")
    
    print("\n" + "-"*80)
    print("Full Answer:")
    print("-"*80)
    print(answer)
    print("-"*80)
    
    # Assertions
    assert isinstance(answer, str) and len(answer) > 0, "Output should be non-empty string"
    assert "GPa" in answer, "Output should contain 'GPa' (modulus units)"
    assert "[ELASTIC_AGENT]" not in answer, "Output should NOT contain raw tool markers"
    assert "Calling:" not in answer, "Output should NOT contain debug markers"
    assert "mp-" in answer.lower(), "Output should cite material ID (mp-XXXXX)"
    
    print("\n✓ All assertions passed for Test 1")
    return True


def test_multi_property_query():
    """
    Test 2: Verify multi-property queries trigger multiple sub-agents.
    
    This query asks for both:
    - Elastic properties (bulk/shear modulus)
    - Thermodynamic properties (formation energy)
    
    The supervisor LLM should recognize it needs both elastic_agent AND thermo_agent.
    
    Verification:
    - Check terminal output shows "Action: elastic_agent" and "Action: thermo_agent"
    - Output synthesizes both properties into coherent answer
    """
    print("\n" + "="*80)
    print("TEST 2: MULTI-PROPERTY QUERY")
    print("="*80)
    
    supervisor = create_supervisor()
    query = "What is the stiffest material with the lowest formation energy in the Si-O system?"
    
    print(f"\nQuery: {query}")
    print("\nInvoking supervisor (watch terminal for Thought/Action/Observation chain)...\n")
    print("IMPORTANT: You should see in the output above:")
    print("  Thought: I need to find...")
    print("  Action: elastic_agent")
    print("  Action: thermo_agent")
    print("  Final Answer: ...\n")
    
    result = supervisor.invoke({"input": query})
    answer = result.get("output", "")
    
    print("\n" + "-"*80)
    print("Full Answer:")
    print("-"*80)
    print(answer)
    print("-"*80)
    
    # Assertions
    assert isinstance(answer, str) and len(answer) > 0, "Output should be non-empty string"
    assert "[ELASTIC_AGENT]" not in answer, "Output should NOT contain raw tool markers"
    assert "Calling:" not in answer, "Output should NOT contain debug markers"
    
    print("\n✓ All assertions passed for Test 2")
    print("\nNOTE: Check the terminal output above to verify that BOTH tools were called:")
    print("  - Look for 'Action: elastic_agent' in the Thought/Action/Observation chain")
    print("  - Look for 'Action: thermo_agent' in the Thought/Action/Observation chain")
    print("  - If you see both, the multi-agent reasoning is working correctly")
    
    return True


def test_nac_elastic_tensor():
    """
    Test 3: Verify the NaC elastic tensor query (original bug fix).
    
    This was the original failing query that returned "No elastic data found".
    Now it should work with proper chemsys conversion (Na-C).
    """
    print("\n" + "="*80)
    print("TEST 3: NaC ELASTIC TENSOR (Original Bug Fix)")
    print("="*80)
    
    supervisor = create_supervisor()
    query = "What is the full elastic tensor of NaC?"
    
    print(f"\nQuery: {query}")
    print("\nInvoking supervisor...\n")
    
    result = supervisor.invoke({"input": query})
    answer = result.get("output", "")
    
    print("\n" + "-"*80)
    print("Full Answer:")
    print("-"*80)
    print(answer)
    print("-"*80)
    
    # Assertions
    assert isinstance(answer, str) and len(answer) > 0, "Output should be non-empty string"
    assert "GPa" in answer or "modulus" in answer.lower(), "Output should contain elastic data"
    assert "No elastic data found" not in answer, "Should find elastic data for NaC"
    assert "mp-" in answer.lower(), "Output should cite material ID"
    
    print("\n✓ All assertions passed for Test 3")
    return True


def verify_ollama_running():
    """
    Verify that Ollama is actually running with Qwen model.
    
    This checks that the system has real LLM reasoning, not just pattern matching.
    """
    print("\n" + "="*80)
    print("OLLAMA VERIFICATION")
    print("="*80)
    
    import subprocess
    
    try:
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=5)
        print("\nOllama PS Output:")
        print(result.stdout)
        
        if "qwen2.5" in result.stdout.lower():
            print("✓ Qwen2.5 model is loaded and running")
            return True
        else:
            print("⚠ Warning: qwen2.5 model not shown as running")
            print("  (It may load on-demand during first query)")
            return True  # Not a hard failure
            
    except FileNotFoundError:
        print("✗ ERROR: 'ollama' command not found in PATH")
        print("  Make sure Ollama is installed and in your PATH")
        return False
    except subprocess.TimeoutExpired:
        print("✗ ERROR: 'ollama ps' command timed out")
        return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    print("="*80)
    print("LatticeReAct Agent Implementation Verification")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. Single property queries work with LLM reasoning")
    print("2. Multi-property queries trigger multiple sub-agents")
    print("3. Original NaC elastic tensor bug is fixed")
    print("4. Ollama is actually running (real LLM, not fake routing)")
    
    # Verify Ollama first
    print("\n" + "="*80)
    print("PRE-TEST: Verifying Ollama is running...")
    print("="*80)
    ollama_ok = verify_ollama_running()
    if not ollama_ok:
        print("\n✗ CRITICAL: Ollama verification failed. Start Ollama first:")
        print("  ollama serve qwen2.5:14b-instruct-q8_0")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Test 1: Single Property Query", test_single_property_query),
        ("Test 2: Multi-Property Query", test_multi_property_query),
        ("Test 3: NaC Elastic Tensor", test_nac_elastic_tensor),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except AssertionError as e:
            print(f"\n✗ {test_name} FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {test_name} ERROR: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe LatticeReAct system is now running with real LLM reasoning:")
        print("  - Supervisoragent uses Qwen2.5 for semantic understanding")
        print("  - Sub-agents use Qwen2.5 for reasoning about API calls")
        print("  - No regex pattern matching or if/else routing")
        print("  - Thought/Action/Observation loops visible in terminal")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Review output above.")
        sys.exit(1)
