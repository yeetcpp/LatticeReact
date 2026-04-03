#!/usr/bin/env python3
"""
Zero-Inference Grounding Verification Test
============================================

This script demonstrates how the Qwen-optimized grounding system prevents 
hallucinated mp-codes by capturing tool observations and verifying the LLM 
output against them.

Usage:
    python3 test_grounding_verification.py
"""

import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

from agents.supervisor import create_supervisor
from tools.verification_middleware import (
    ZeroInferenceVerifier, 
    ToolObservationCapture,
)


def test_grounding_verification():
    """Test the grounding verification system."""
    
    print("\n" + "=" * 90)
    print("ZERO-INFERENCE GROUNDING VERIFICATION TEST")
    print("=" * 90)
    print("\nInitializing supervisor with grounded system prompt...")
    
    # Create supervisor (now with grounded prompt)
    supervisor = create_supervisor()
    print("✓ Supervisor initialized with Zero-Inference Grounding constraints")
    
    # Test Query: Bandgaps (the problematic case from earlier)
    test_query = "What are the bandgaps of these materials: Si, Ge, GaAs, GaN, SiC? Only ground-state bandgaps."
    
    print("\n" + "=" * 90)
    print(f"QUERY: {test_query}")
    print("=" * 90)
    
    # Clear observation capture
    ToolObservationCapture.clear()
    print("✓ Observation capture initialized")
    
    # Run the supervisor
    print("\nRunning supervisor agent...")
    print("(This will make tool calls and capture all observations)\n")
    
    result = supervisor.invoke({"input": test_query})
    llm_output = result.get("output", "")
    
    print("\n" + "=" * 90)
    print("LLM OUTPUT (Final Answer):")
    print("=" * 90)
    print(llm_output)
    
    # Get all tool observations
    tool_observations = ToolObservationCapture.get_all()
    
    print("\n" + "=" * 90)
    print("CAPTURED TOOL OBSERVATIONS")
    print("=" * 90)
    print(f"Total observations captured: {len(tool_observations)}\n")
    
    if tool_observations:
        for i, obs in enumerate(tool_observations, 1):
            preview = obs[:200] + "..." if len(obs) > 200 else obs
            print(f"[{i}] Tool Output Preview:")
            print(f"    {preview}\n")
    else:
        print("⚠️  No tool observations captured. Tools may not have been called.")
    
    # Run verification
    print("\n" + "=" * 90)
    print("RUNNING GROUNDING VERIFICATION")
    print("=" * 90 + "\n")
    
    verification = ZeroInferenceVerifier.verify(
        query=test_query,
        llm_output=llm_output,
        tool_observations=tool_observations
    )
    
    # Print detailed report
    print(verification)
    
    # Summary statistics
    print("\n" + "=" * 90)
    print("VERIFICATION SUMMARY")
    print("=" * 90)
    print(f"\nmp-codes in LLM output:     {verification.llm_mp_codes or '[NONE]'}")
    print(f"mp-codes from tools:       {verification.observed_mp_codes or '[NONE]'}")
    print(f"\nVerified (grounded):       {verification.verified_codes or '[NONE]'}")
    print(f"Hallucinated (NOT grounded): {verification.hallucinated_codes or '[NONE]'}")
    print(f"Missing (in tools but not in LLM answer): {verification.missing_codes or '[NONE]'}")
    
    if verification.is_fully_grounded:
        print("\n✓✓✓ SUCCESS: LLM output is fully grounded in tool observations!")
    else:
        print(f"\n✗✗✗ FAILURE: LLM hallucinated {len(verification.hallucinated_codes)} mp-code(s)")
        print("    These mp-codes appear in the LLM answer but NOT in tool outputs:")
        for code in verification.hallucinated_codes:
            print(f"      - {code}")
    
    # Diagnostic recommendations
    print("\n" + "=" * 90)
    print("DIAGNOSTIC RECOMMENDATIONS")
    print("=" * 90)
    
    if not verification.is_fully_grounded:
        print("\n⚠️  Hallucination Detected. Recommended diagnostics:")
        print("\n1. CHECK LLM PROMPT: Verify the system prompt includes THE VERBATIM RULE")
        print("   Location: agents/supervisor.py, system_prompt variable")
        print("   Required: 'You are FORBIDDEN from generating any string starting with mp-'")
        
        print("\n2. CHECK <thought> TAGS: In the verbose output above, look for:")
        print("   <thought>")
        print("     Tool observations analysis:")
        print("     - mp-codes in tool output: [explicit inventory]")
        print("   </thought>")
        print("   If not present, the LLM is not following the structured thinking constraint.")
        
        print("\n3. INCREASE TEMPERATURE?: Current temperature is 0 (deterministic)")
        print("   If LLM is still hallucinating at T=0, the issue is in prompt adherence, not randomness.")
        
        print("\n4. TEST WITH SIMPLE QUERY: Try a single-material query:")
        print("   'What is the bandgap of Silicon (element Si)?'")
        print("   This narrows down whether the issue is multi-material confusion.")
        
        print("\n5. MANUAL VERIFICATION: For each hallucinated mp-code:")
        for code in verification.hallucinated_codes:
            print(f"   - Search Materials Project database for {code}")
            print(f"     Was this code in ANY tool observation? {code in ''.join(tool_observations)}")
    
    else:
        print("\n✓ All mp-codes are properly grounded. System is working correctly!")
        print("\nNext steps:")
        print("  1. Run comparative tests with the OLD system prompt")
        print("  2. Verify that this grounded version has NO hallucinations")
        print("  3. Measure latency impact (structured thinking may increase tokens)")
    
    return verification


def test_individual_bandgap_queries():
    """Test individual material queries to isolate hallucinations."""
    
    print("\n\n" + "=" * 90)
    print("INDIVIDUAL MATERIAL TEST")
    print("=" * 90)
    
    supervisor = create_supervisor()
    materials = ["Silicon", "Germanium", "GaAs", "GaN", "SiC"]
    
    for material in materials:
        query = f"What is the bandgap of {material}? Give the mp-code and phase information."
        
        print(f"\n--- Testing {material} ---")
        print(f"Query: {query}")
        
        ToolObservationCapture.clear()
        result = supervisor.invoke({"input": query})
        
        output = result.get("output", "")
        print(f"Output (first 300 chars): {output[:300]}...")
        
        # Quick verification
        observations = ToolObservationCapture.get_all()
        verification = ZeroInferenceVerifier.verify(query, output, observations)
        
        if verification.hallucinated_codes:
            print(f"⚠️  HALLUCINATED: {verification.hallucinated_codes}")
        else:
            print(f"✓ GROUNDED: All codes verified")


if __name__ == "__main__":
    try:
        # Run main test
        verification = test_grounding_verification()
        
        # Run individual tests (optional - commented out to save time)
        # Uncomment to run:
        # test_individual_bandgap_queries()
        
        # Final summary
        print("\n\n" + "=" * 90)
        print("TEST COMPLETE")
        print("=" * 90)
        print(f"\nFinal Status: {'✓ GROUNDED' if verification.is_fully_grounded else '✗ HALLUCINATIONS DETECTED'}")
        print("\nNext Action: Review diagnostic recommendations above")
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
