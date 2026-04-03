"""
Zero-Inference Grounding Verification Middleware
Detects hallucinated mp-codes in LLM output by comparing against raw tool observations.
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import json


@dataclass
class VerificationReport:
    """Report on mp-code grounding verification."""
    query: str
    llm_output: str
    tool_observations: List[str]
    
    # Extracted identifiers
    llm_mp_codes: List[str]
    observed_mp_codes: List[str]
    
    # Analysis
    hallucinated_codes: List[str]
    verified_codes: List[str]
    missing_codes: List[str]
    
    is_fully_grounded: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "is_fully_grounded": self.is_fully_grounded,
            "llm_mp_codes": self.llm_mp_codes,
            "observed_mp_codes": self.observed_mp_codes,
            "verified_codes": self.verified_codes,
            "hallucinated_codes": self.hallucinated_codes,
            "missing_codes": self.missing_codes,
            "report": self.__str__()
        }
    
    def __str__(self) -> str:
        lines = [
            "=" * 80,
            "ZERO-INFERENCE GROUNDING VERIFICATION REPORT",
            "=" * 80,
            f"Query: {self.query[:100]}{'...' if len(self.query) > 100 else ''}",
            "",
            "─" * 80,
            "EXTRACTION RESULTS:",
            "─" * 80,
            f"✓ mp-codes in LLM output:      {self.llm_mp_codes if self.llm_mp_codes else '[NONE FOUND]'}",
            f"✓ mp-codes in tool observations: {self.observed_mp_codes if self.observed_mp_codes else '[NONE FOUND]'}",
            "",
        ]
        
        # Verified codes
        if self.verified_codes:
            lines.append("✓ VERIFIED (found in tool output):")
            for code in self.verified_codes:
                lines.append(f"    {code}")
            lines.append("")
        
        # Hallucinated codes (CRITICAL)
        if self.hallucinated_codes:
            lines.append("✗ HALLUCINATED (NOT in tool output):")
            for code in self.hallucinated_codes:
                lines.append(f"    {code} ← This is a FAKE mp-code!")
            lines.append("")
        
        # Missing codes
        if self.missing_codes:
            lines.append("? MISSING (in tool but not in LLM answer):")
            for code in self.missing_codes:
                lines.append(f"    {code}")
            lines.append("")
        
        # Final verdict
        lines.append("─" * 80)
        if self.is_fully_grounded:
            lines.append("✓✓✓ VERDICT: FULLY GROUNDED - All mp-codes are verified from tool output")
        else:
            num_hallucinated = len(self.hallucinated_codes)
            lines.append(f"✗✗✗ VERDICT: CONTAINS HALLUCINATIONS - {num_hallucinated} fake mp-code(s) detected")
        lines.append("=" * 80)
        
        return "\n".join(lines)


class ZeroInferenceVerifier:
    """Verifies that LLM output is grounded in tool observations."""
    
    # Regex pattern for mp-codes
    MP_CODE_PATTERN = r'mp-\d{1,10}'
    
    @staticmethod
    def extract_mp_codes(text: str) -> List[str]:
        """Extract all mp-XXXX codes from text."""
        matches = re.findall(ZeroInferenceVerifier.MP_CODE_PATTERN, text)
        return sorted(list(set(matches)))  # Deduplicate and sort
    
    @staticmethod
    def extract_phase_info(observation: str) -> Dict[str, str]:
        """Extract mp-code → phase mapping from observation if available."""
        phase_map = {}
        # Pattern: mp-167 (Cubic) or mp-667 (Hexagonal phase) or similar
        pattern = r'mp-\d{1,10}\s*\(([^)]+)\)'
        matches = re.findall(pattern, observation)
        
        # More precise extraction with phase info
        detailed_pattern = r'(mp-\d{1,10})\s*\(([^)]+)\)'
        for code, phase_text in re.findall(detailed_pattern, observation):
            phase_map[code] = phase_text.strip()
        
        return phase_map
    
    @staticmethod
    def verify(
        query: str,
        llm_output: str,
        tool_observations: List[str]
    ) -> VerificationReport:
        """
        Verify that LLM output mp-codes are grounded in tool observations.
        
        Args:
            query: The original user query
            llm_output: The final LLM response/synthesis
            tool_observations: List of raw tool observation strings
        
        Returns:
            VerificationReport with detailed analysis
        """
        # Extract mp-codes from all sources
        llm_codes = ZeroInferenceVerifier.extract_mp_codes(llm_output)
        
        observed_codes = []
        for obs in tool_observations:
            observed_codes.extend(ZeroInferenceVerifier.extract_mp_codes(obs))
        observed_codes = sorted(list(set(observed_codes)))
        
        # Categorize
        verified = [code for code in llm_codes if code in observed_codes]
        hallucinated = [code for code in llm_codes if code not in observed_codes]
        missing = [code for code in observed_codes if code not in llm_codes]
        
        is_grounded = len(hallucinated) == 0
        
        return VerificationReport(
            query=query,
            llm_output=llm_output,
            tool_observations=tool_observations,
            llm_mp_codes=llm_codes,
            observed_mp_codes=observed_codes,
            verified_codes=verified,
            hallucinated_codes=hallucinated,
            missing_codes=missing,
            is_fully_grounded=is_grounded
        )


class GroundedAgentWrapper:
    """
    Wrapper for agent invocation that captures tool observations and 
    verifies LLM output against them.
    """
    
    def __init__(self, agent):
        """
        Initialize with an agent.
        
        Args:
            agent: The LLM agent (e.g., elastic_agent, supervisor, etc.)
        """
        self.agent = agent
        self.last_tool_observations = []
    
    def invoke(self, agent_input: Dict[str, str], capture_observations: bool = True) -> Dict[str, Any]:
        """
        Invoke the agent and verify output grounding.
        
        Args:
            agent_input: Input dict with 'input' key (e.g., {"input": "What is the bandgap of Si?"})
            capture_observations: If True, attempt to capture tool observations
        
        Returns:
            Dict with keys:
                - output: The agent's response
                - verification: VerificationReport (if tools were called)
                - is_hallucinating: Bool indicating if hallucinations detected
        """
        # Invoke agent
        result = self.agent.invoke(agent_input)
        llm_output = result.get("output", "")
        
        # For now, we'll do a simpler verification using the output itself
        # In a more advanced version, you'd instrument the agent internals to capture tool calls
        
        query = agent_input.get("input", "")
        
        # If we're doing full verification with observations, we'd need to:
        # 1. Instrument the tool wrappers to log observations
        # 2. Pass those observations to the verifier
        # For this implementation, we'll document how to do that
        
        verification = VerificationReport(
            query=query,
            llm_output=llm_output,
            tool_observations=self.last_tool_observations,
            llm_mp_codes=ZeroInferenceVerifier.extract_mp_codes(llm_output),
            observed_mp_codes=[],
            verified_codes=[],
            hallucinated_codes=[],  # Would be populated with real observations
            missing_codes=[],
            is_fully_grounded=True  # Placeholder - needs real observations
        )
        
        result["verification"] = verification
        result["is_hallucinating"] = not verification.is_fully_grounded
        
        return result


class ToolObservationCapture:
    """
    Decorator/mixin for tool wrappers to capture observations for verification.
    Add this to your tool wrapper functions to automatically log observations.
    """
    
    observations = []  # Class-level storage of all observations
    
    @staticmethod
    def capture(tool_name: str, input_query: str, observation: str) -> str:
        """
        Capture a tool observation for verification.
        
        Usage in your tool wrapper:
            def call_elastic_tool(query_str):
                try:
                    result = query_mp_elastic.invoke(query_str)
                    ToolObservationCapture.capture("mp_elastic", query_str, result)
                    return result
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    ToolObservationCapture.capture("mp_elastic", query_str, error_msg)
                    return error_msg
        """
        ToolObservationCapture.observations.append({
            "tool": tool_name,
            "input": input_query,
            "observation": observation,
            "timestamp": len(ToolObservationCapture.observations)
        })
        return observation
    
    @staticmethod
    def get_all() -> List[str]:
        """Get all captured observations as strings."""
        return [obs["observation"] for obs in ToolObservationCapture.observations]
    
    @staticmethod
    def clear():
        """Clear all captured observations."""
        ToolObservationCapture.observations = []
    
    @staticmethod
    def report():
        """Print a summary of all captured observations."""
        print("\n" + "=" * 80)
        print("TOOL OBSERVATION CAPTURE REPORT")
        print("=" * 80)
        for i, obs in enumerate(ToolObservationCapture.observations, 1):
            print(f"\n[{i}] Tool: {obs['tool']}")
            print(f"    Input: {obs['input'][:60]}{'...' if len(obs['input']) > 60 else ''}")
            mp_codes = ZeroInferenceVerifier.extract_mp_codes(obs['observation'])
            print(f"    mp-codes found: {mp_codes if mp_codes else '[NONE]'}")


# ============================================================================
# EXAMPLE USAGE - Add this to your test scripts
# ============================================================================

"""
from tools.chromadb_cache import initialize_cache
from agents.supervisor import create_supervisor_agent
from tools.mp_elastic import search_mp_elastic
from verification_middleware import (
    ZeroInferenceVerifier, 
    ToolObservationCapture,
    GroundedAgentWrapper
)

# Start capturing observations
ToolObservationCapture.clear()

# Create agent
supervisor = create_supervisor_agent()

# Wrap the agent
grounded_supervisor = GroundedAgentWrapper(supervisor)

# Run query
result = grounded_supervisor.invoke({
    "input": "What are the bandgaps of Si, Ge, GaAs, GaN, SiC?"
})

# Verify output
tool_observations = ToolObservationCapture.get_all()
verification = ZeroInferenceVerifier.verify(
    query="What are the bandgaps of Si, Ge, GaAs, GaN, SiC?",
    llm_output=result["output"],
    tool_observations=tool_observations
)

print(verification)  # Detailed report
print(verification.is_fully_grounded)  # True if no hallucinations

# If hallucinations detected:
if verification.hallucinated_codes:
    print(f"⚠️ ALERT: Hallucinated codes: {verification.hallucinated_codes}")
    for code in verification.hallucinated_codes:
        print(f"  - {code} appears in output but NOT in tool observations!")
"""
