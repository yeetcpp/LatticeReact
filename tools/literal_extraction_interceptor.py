"""
LITERAL-EXTRACTION INTERCEPTOR MIDDLEWARE
==========================================

This module provides the Python guardrail for enforcing 100% mp-code accuracy
in agent responses. It intercepts agent output before returning to users and
verifies that all mp-codes are grounded in tool observations.

Author: AI Engineer
Framework: Framework-agnostic (pure Python, regex, standard library only)
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class InterceptionStatus(Enum):
    """Status codes for interception validation."""
    GROUNDED = "GROUNDED"  # All codes verified
    HALLUCINATED = "HALLUCINATED"  # One or more codes not in observation
    ERROR = "ERROR"  # Validation error
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"  # Max retries reached


@dataclass
class InterceptionResult:
    """Result of interception validation."""
    status: InterceptionStatus
    agent_response: str
    tool_observation: str
    hallucinated_ids: List[str]
    grounded_ids: List[str]
    is_valid: bool
    error_message: str = ""
    
    def __str__(self) -> str:
        """Pretty-print the interception result."""
        lines = [
            "╔" + "═" * 78 + "╗",
            "║ LITERAL-EXTRACTION INTERCEPTION RESULT" + " " * 38 + "║",
            "╚" + "═" * 78 + "╝",
            "",
            f"Status: {self.status.value}",
            f"Valid: {'✓ YES' if self.is_valid else '✗ NO'}",
            ""
        ]
        
        if self.grounded_ids:
            lines.append(f"✓ Grounded IDs ({len(self.grounded_ids)}):")
            for mp_id in sorted(self.grounded_ids):
                lines.append(f"    {mp_id}")
            lines.append("")
        
        if self.hallucinated_ids:
            lines.append(f"✗ HALLUCINATED IDs ({len(self.hallucinated_ids)}):")
            for mp_id in sorted(self.hallucinated_ids):
                lines.append(f"    {mp_id} ← NOT FOUND IN OBSERVATION")
            lines.append("")
        
        if self.error_message:
            lines.append(f"Error: {self.error_message}")
            lines.append("")
        
        return "\n".join(lines)


class LiteralExtractionInterceptor:
    """
    Framework-agnostic interceptor for validating mp-code literal extraction.
    
    This class provides the core validation logic without any dependencies on
    LangChain, Ollama, or other frameworks. It uses only regex and string ops.
    """
    
    # Regex pattern to find all mp-codes
    MP_CODE_PATTERN = r'mp-\d{1,10}'
    
    @staticmethod
    def extract_mp_codes(text: str) -> List[str]:
        """Extract all mp-XXXX codes from text, return sorted unique list."""
        if not text:
            return []
        matches = re.findall(LiteralExtractionInterceptor.MP_CODE_PATTERN, text)
        return sorted(list(set(matches)))
    
    @staticmethod
    def validate_response(
        agent_response: str,
        tool_observation: str
    ) -> InterceptionResult:
        """
        Validate that all mp-codes in agent response exist in tool observation.
        
        Args:
            agent_response: The agent's final answer/synthesis
            tool_observation: The raw tool observation with ground-truth mp-codes
        
        Returns:
            InterceptionResult with validation details
        """
        
        # Extract codes from both sources
        response_codes = LiteralExtractionInterceptor.extract_mp_codes(agent_response)
        observation_codes = LiteralExtractionInterceptor.extract_mp_codes(tool_observation)
        
        # Identify grounded vs hallucinated
        grounded = [code for code in response_codes if code in observation_codes]
        hallucinated = [code for code in response_codes if code not in observation_codes]
        
        # Determine status
        is_valid = len(hallucinated) == 0
        status = InterceptionStatus.GROUNDED if is_valid else InterceptionStatus.HALLUCINATED
        
        # Build error message if hallucinations detected
        error_message = ""
        if hallucinated:
            error_message = (
                f"SYSTEM INTERCEPT: You hallucinated {len(hallucinated)} mp-code(s). "
                f"These IDs do not appear in the tool observation:\n"
            )
            for code in hallucinated:
                error_message += f"  - {code}\n"
            error_message += (
                "\nRe-read the tool observation and use ONLY the exact mp-codes provided. "
                "Do not synthesize IDs from memory."
            )
        
        return InterceptionResult(
            status=status,
            agent_response=agent_response,
            tool_observation=tool_observation,
            hallucinated_ids=hallucinated,
            grounded_ids=grounded,
            is_valid=is_valid,
            error_message=error_message
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SCAFFOLDING EXAMPLE: RETRY LOOP WITH MAX RETRIES
# ═══════════════════════════════════════════════════════════════════════════════

def scaffold_validate_and_retry_agent(
    agent,
    query: str,
    tool_observation: str,
    max_retries: int = 3
) -> Tuple[str, bool]:
    """
    SCAFFOLDING EXAMPLE: Shows retry loop structure.
    
    This is meant to demonstrate the control flow before showing the
    production-ready implementation below.
    
    Args:
        agent: The LLM agent with .invoke() method
        query: The original user query
        tool_observation: The tool observation with ground-truth mp-codes
        max_retries: Maximum retry attempts (default 3)
    
    Returns:
        Tuple of (final_response, is_grounded)
    
    Example:
        response, grounded = scaffold_validate_and_retry_agent(
            supervisor,
            query="What is the bandgap of Si?",
            tool_observation="[mp-149] Si: 1.20 eV",
            max_retries=3
        )
        if not grounded:
            print("Could not ground response after 3 attempts")
    """
    
    print(f"\n{'='*80}")
    print(f"SCAFFOLD: Validate-and-Retry Pattern (max_retries={max_retries})")
    print(f"{'='*80}")
    
    for attempt in range(1, max_retries + 1):
        print(f"\n[Attempt {attempt}/{max_retries}]")
        
        # Step 1: Get agent response
        print("→ Invoking agent...")
        result = agent.invoke({"input": query})
        agent_response = result.get("output", str(result))
        print(f"✓ Agent response received ({len(agent_response)} chars)")
        
        # Step 2: Validate using interceptor
        print("→ Validating response against tool observation...")
        validation = LiteralExtractionInterceptor.validate_response(
            agent_response,
            tool_observation
        )
        print(validation)
        
        # Step 3: Check if valid
        if validation.is_valid:
            print(f"\n✓✓✓ SUCCESS on attempt {attempt}")
            return agent_response, True
        
        # Step 4: If invalid and retries remain, prepare retry
        if attempt < max_retries:
            print(f"\n⚠️  Hallucination detected. Retrying with corrected prompt...")
            
            # Construct retry prompt with explicit constraint
            retry_prompt = (
                f"{query}\n\n"
                f"[SYSTEM INTERCEPT - RETRY {attempt}]\n"
                f"Your previous response contained hallucinated mp-codes:\n"
            )
            for bad_id in validation.hallucinated_ids:
                retry_prompt += f"  - {bad_id} (NOT in tool observation)\n"
            
            retry_prompt += (
                f"\nThese are the ONLY mp-codes in the tool observation:\n"
                f"{', '.join(LiteralExtractionInterceptor.extract_mp_codes(tool_observation))}\n"
                f"\nUse ONLY these exact codes. Do not synthesize new ones."
            )
            
            # Update query for next iteration
            query = retry_prompt
            print(f"→ Retry query prepared with constraints")
        else:
            print(f"\n✗✗✗ Max retries ({max_retries}) exhausted")
            print(f"Could not ground response. Returning best attempt.")
            return agent_response, False
    
    # Fallback
    return agent_response, False


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTION: VALIDATE_AND_RETRY_AGENT (FINAL IMPLEMENTATION)
# ═══════════════════════════════════════════════════════════════════════════════

def validate_and_retry_agent(
    agent,
    query: str,
    tool_observation: str,
    max_retries: int = 3,
    verbose: bool = False
) -> Dict:
    """
    PRODUCTION IMPLEMENTATION: Validate agent response and retry on hallucination.
    
    This function acts as middleware between the agent and the user. It:
    1. Calls the agent with the query
    2. Validates all mp-codes against the tool observation
    3. If hallucinations detected, retries with corrected prompt (max 3 times)
    4. Returns detailed result with validation metadata
    
    Args:
        agent: The LLM agent with .invoke({"input": ...}) method
        query: The original user query
        tool_observation: The tool observation with ground-truth mp-codes
        max_retries: Maximum validation-retry attempts (default 3)
        verbose: If True, print detailed output during process
    
    Returns:
        Dict with keys:
            - response: Final agent response
            - is_grounded: Boolean indicating if response is fully grounded
            - attempt: Which attempt succeeded (1-N or None if exhausted)
            - validations: List of all InterceptionResult objects from each attempt
            - hallucinated_ids: List of any hallucinated codes (empty if grounded)
            - grounded_ids: List of all verified mp-codes
    
    Example:
        >>> from agents.supervisor import create_supervisor
        >>> supervisor = create_supervisor()
        >>> tool_obs = "[mp-149] Si: 1.20 eV\\n[mp-32] Ge: 0.67 eV"
        >>> result = validate_and_retry_agent(
        ...     supervisor,
        ...     "What are bandgaps of Si and Ge?",
        ...     tool_obs,
        ...     max_retries=3,
        ...     verbose=True
        ... )
        >>> print(f"Grounded: {result['is_grounded']}")
        >>> print(f"Hallucinated: {result['hallucinated_ids']}")
    """
    
    validations = []
    current_query = query
    grounding_codes = LiteralExtractionInterceptor.extract_mp_codes(tool_observation)
    
    if verbose:
        print("\n" + "=" * 80)
        print("VALIDATE-AND-RETRY AGENT")
        print("=" * 80)
        print(f"Original query: {query[:60]}...")
        print(f"Ground-truth mp-codes: {grounding_codes}")
        print(f"Max retries: {max_retries}")
    
    for attempt in range(1, max_retries + 1):
        if verbose:
            print(f"\n--- Attempt {attempt}/{max_retries} ---")
        
        # Call agent
        try:
            result = agent.invoke({"input": current_query})
            agent_response = result.get("output", str(result))
        except Exception as e:
            if verbose:
                print(f"⚠️  Agent invocation failed: {e}")
            agent_response = f"ERROR: {str(e)}"
        
        # Validate
        validation = LiteralExtractionInterceptor.validate_response(
            agent_response,
            tool_observation
        )
        validations.append(validation)
        
        if verbose:
            print(f"Response length: {len(agent_response)}")
            print(f"mp-codes found: {validation.grounded_ids + validation.hallucinated_ids}")
            if validation.hallucinated_ids:
                print(f"✗ Hallucinated: {validation.hallucinated_ids}")
            else:
                print(f"✓ All codes verified")
        
        # Check if valid
        if validation.is_valid:
            if verbose:
                print(f"\n✓✓✓ SUCCESS on attempt {attempt}")
            
            return {
                "response": agent_response,
                "is_grounded": True,
                "attempt": attempt,
                "validations": validations,
                "hallucinated_ids": [],
                "grounded_ids": validation.grounded_ids,
                "status": "GROUNDED"
            }
        
        # Prepare retry prompt if retries remain
        if attempt < max_retries:
            current_query = _construct_retry_prompt(
                original_query=query,
                hallucinated_ids=validation.hallucinated_ids,
                grounding_codes=grounding_codes,
                attempt_number=attempt,
                tool_observation=tool_observation
            )
            
            if verbose:
                print(f"⚠️  Hallucinations detected. Preparing retry...")
    
    # Max retries exhausted
    if verbose:
        print(f"\n✗✗✗ Max retries ({max_retries}) exhausted")
        print(f"Returning best attempt with hallucinations present.")
    
    # Return the first validation (which had the most hallucinations we tried to fix)
    final_validation = validations[0]  # Or could return last, your choice
    
    return {
        "response": final_validation.agent_response,
        "is_grounded": False,
        "attempt": None,
        "validations": validations,
        "hallucinated_ids": final_validation.hallucinated_ids,
        "grounded_ids": final_validation.grounded_ids,
        "status": "RETRY_EXHAUSTED"
    }


def _construct_retry_prompt(
    original_query: str,
    hallucinated_ids: List[str],
    grounding_codes: List[str],
    attempt_number: int,
    tool_observation: str
) -> str:
    """
    Construct a retry prompt that feeds back validation results to the agent.
    
    This is a private helper that creates the corrected prompt for the next retry.
    """
    
    retry_prompt = f"""{original_query}

╔══ SYSTEM INTERCEPT (Attempt {attempt_number}) ══╗

Your previous response contained HALLUCINATED mp-codes:
{chr(10).join(f"  ✗ {code}" for code in hallucinated_ids)}

These codes DO NOT appear in the tool observation.

═══════════════════════════════════════════════════════════════════════════════

TRUTH: The tool observation contains ONLY these mp-codes:
{', '.join(grounding_codes)}

YOU MUST:
1. Re-read the tool observation carefully
2. Use ONLY and ALL the mp-codes listed above
3. Do NOT synthesize new mp-codes
4. If a material is not in the observation, state ID_NOT_FOUND
5. Use <thought> tags to show your mp-code extraction process

Tool Observation (for reference):
{tool_observation}

Now provide your corrected answer using ONLY the verified mp-codes above."""
    
    return retry_prompt


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

"""
EXAMPLE 1: Basic Usage
─────────────────────

from agents.supervisor import create_supervisor

supervisor = create_supervisor()
tool_observation = "[mp-149] Si: 1.20 eV\\n[mp-32] Ge: 0.67 eV"

result = validate_and_retry_agent(
    agent=supervisor,
    query="What are bandgaps of Si and Ge?",
    tool_observation=tool_observation,
    max_retries=3,
    verbose=True
)

if result['is_grounded']:
    print(f"✓ Grounded answer: {result['response']}")
else:
    print(f"✗ Could not ground. Hallucinated: {result['hallucinated_ids']}")


EXAMPLE 2: In a FastAPI Endpoint
──────────────────────────────

@app.post("/materials/query")
async def material_query(user_query: str, tool_observation: str):
    result = validate_and_retry_agent(
        agent=supervisor,
        query=user_query,
        tool_observation=tool_observation,
        max_retries=3,
        verbose=False  # Don't print in production
    )
    
    return {
        "answer": result["response"],
        "grounded": result["is_grounded"],
        "hallucinated": result["hallucinated_ids"],
        "attempts": len(result["validations"])
    }


EXAMPLE 3: Batch Validation
────────────────────────

queries = [
    ("What's the bandgap of Si?", "[mp-149] Si: 1.20 eV"),
    ("What's the bandgap of Ge?", "[mp-32] Ge: 0.67 eV"),
    ("What's the bandgap of GaAs?", "[mp-2534] GaAs: 1.43 eV"),
]

for query, obs in queries:
    result = validate_and_retry_agent(
        supervisor, query, obs, max_retries=2
    )
    status = "✓ GROUNDED" if result['is_grounded'] else "✗ HALLUCINATED"
    print(f"{status}: {query}")
    if not result['is_grounded']:
        print(f"  Hallucinated: {result['hallucinated_ids']}")


EXAMPLE 4: Direct Validation Only (No Agent Call)
───────────────────────────────────────────────

# Sometimes you just want to validate a response you already have:

existing_response = "Silicon (Si) [mp-149]: 1.20 eV. Germanium (Ge) [mp-32]: 0.67 eV."
tool_obs = "[mp-149] Si: 1.20 eV\\n[mp-32] Ge: 0.67 eV"

validation = LiteralExtractionInterceptor.validate_response(
    existing_response,
    tool_obs
)

print(validation)
if not validation.is_valid:
    print(f"Hallucinated: {validation.hallucinated_ids}")
"""


if __name__ == "__main__":
    # Quick test of the interceptor
    print("\n" + "=" * 80)
    print("LITERAL-EXTRACTION INTERCEPTOR TEST")
    print("=" * 80)
    
    # Test case 1: Fully grounded response
    print("\n[Test 1] Fully Grounded Response")
    print("-" * 80)
    
    good_response = "Silicon (Si) [mp-149]: 1.20 eV. Germanium (Ge) [mp-32]: 0.67 eV."
    tool_obs = "[mp-149] Si: 1.20 eV\n[mp-32] Ge: 0.67 eV"
    
    result = LiteralExtractionInterceptor.validate_response(good_response, tool_obs)
    print(result)
    assert result.is_valid, "Test 1 failed: Should be grounded"
    
    # Test case 2: Hallucinated mp-codes
    print("\n[Test 2] Hallucinated mp-codes")
    print("-" * 80)
    
    bad_response = "Silicon (Si) [mp-149]: 1.20 eV. Germanium (Ge) [mp-999]: 0.67 eV."
    result = LiteralExtractionInterceptor.validate_response(bad_response, tool_obs)
    print(result)
    assert not result.is_valid, "Test 2 failed: Should detect hallucination"
    assert "mp-999" in result.hallucinated_ids, "Test 2 failed: Should identify mp-999"
    
    # Test case 3: Mixed grounded and hallucinated
    print("\n[Test 3] Mixed Grounded and Hallucinated")
    print("-" * 80)
    
    mixed_response = "Si [mp-149], Ge [mp-32], GaAs [mp-9999]"
    result = LiteralExtractionInterceptor.validate_response(mixed_response, tool_obs)
    print(result)
    assert not result.is_valid, "Test 3 failed: Should detect mixed hallucination"
    
    print("\n" + "=" * 80)
    print("✓ All tests passed!")
    print("=" * 80)
