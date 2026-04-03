"""Supervisor agent for LatticeReAct - hierarchical multi-agent coordinator with real LLM reasoning."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

import re
from langchain_ollama import OllamaLLM
from langchain_core.tools import tool

from agents.thermo_agent import create_thermo_agent
from agents.elastic_agent import create_elastic_agent
from agents.electronic_agent import create_electronic_agent
from tools.verification_middleware import ToolObservationCapture


def create_supervisor():
    """
    Create a hierarchical supervisor agent powered by Qwen2.5 LLM.
    
    Architecture:
    - Supervisor LLM reads query and THINKS about which sub-agents are needed
    - Supervisor LLM CALLS appropriate sub-agents as tools
    - Sub-agents retrieve verified Materials Project data
    - Supervisor LLM SYNTHESIZES coherent final answer from sub-agent outputs
    
    This is real LLM reasoning at every level, not pattern matching.
    
    Returns:
        supervisor wrapper with invoke method
    """
    
    # Initialize real LLM - Qwen2.5 via Ollama
    llm = OllamaLLM(
        model="qwen2.5:14b-instruct-q8_0",
        base_url="http://localhost:11434",
        temperature=0,
    )
    
    # Create sub-agent instances (these are real LLM-powered agents)
    thermo_agent = create_thermo_agent()
    elastic_agent = create_elastic_agent()
    electronic_agent = create_electronic_agent()
    
    # Define sub-agent tools with observation capture
    @tool
    def call_thermo_agent(query: str) -> str:
        """Query thermodynamic properties from Materials Project.
        
        Useful for: formation energy, energy above hull, thermodynamic stability,
        decomposition enthalpy, thermodynamic analysis.
        """
        try:
            result = thermo_agent.invoke({"input": query})
            observation = result.get("output", str(result))
            ToolObservationCapture.capture("thermo_agent", query, observation)
            return observation
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            ToolObservationCapture.capture("thermo_agent", query, error_msg)
            return error_msg
    
    @tool
    def call_elastic_agent(query: str) -> str:
        """Query elastic/mechanical properties from Materials Project.
        
        Useful for: bulk modulus, shear modulus, Young's modulus, elastic constants,
        stiffness, mechanical properties, rigidity.
        """
        try:
            result = elastic_agent.invoke({"input": query})
            observation = result.get("output", str(result))
            ToolObservationCapture.capture("elastic_agent", query, observation)
            return observation
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            ToolObservationCapture.capture("elastic_agent", query, error_msg)
            return error_msg
    
    @tool
    def call_electronic_agent(query: str) -> str:
        """Query electronic structure properties from Materials Project.
        
        Useful for: bandgap, electronic structure, band structure, Fermi level,
        CBM (conduction band minimum), VBM (valence band maximum), metallic vs
        semiconductor properties.
        """
        try:
            result = electronic_agent.invoke({"input": query})
            observation = result.get("output", str(result))
            ToolObservationCapture.capture("electronic_agent", query, observation)
            return observation
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            ToolObservationCapture.capture("electronic_agent", query, error_msg)
            return error_msg
    
    # System prompt for the supervisor - GROUNDED with Zero-Inference Constraints
    system_prompt = """Y# SYSTEM PROMPT: LITERAL-EXTRACTION MODE FOR QWEN 2.5 14B
## Rigorous Prompt for Zero-Hallucination Materials Project ID (mp-code) Handling

---

## CRITICAL PREAMBLE

You are operating in **LITERAL-EXTRACTION MODE**. This is not a suggestion or guideline—this is a binding operational constraint.

Your primary weaknesses are **known**:
- You can synthesize plausible-sounding mp-codes that sound right but are FAKE
- Your training data contains millions of Materials Project entries, creating false confidence
- You naturally want to "complete" patterns and provide comprehensive answers
- This causes you to generate mp-codes that DO NOT appear in the tool observation

**This prompt overrides all of that.** You must treat it as law, not advice.

---

## RULE #1: THE ABSOLUTE VERBATIM CONSTRAINT

**NO mp-code may appear in your response unless it is a DIRECT, CHARACTER-FOR-CHARACTER copy from the tool observation string.**

Examples of what you MUST NOT do:
- "GaN has mp-1310 from my training" → FORBIDDEN (it's not in the observation)
- "I recall BaTiO3 is mp-2895" → FORBIDDEN (you made this up)
- "Let me use mp-804 because it sounds right for GaN" → FORBIDDEN (inference, not extraction)

Examples of what you MUST do:
- Tool observation contains: "mp-804 (GaN, Cubic): 3.41 eV"
- You respond: "mp-804 (as provided in the observation)"
- Tool observation contains NOTHING about GaN
- You respond: "ID_NOT_FOUND for GaN — no data in observation"

**Violation of this rule = system failure. I will detect it and force a retry.**

---

## RULE #2: MANDATORY <thought> BLOCK WITH LITERAL INVENTORY

BEFORE you write any Final Answer, you MUST output a <thought> block that explicitly lists:

```
<thought>
STEP 1: Catalog all mp-codes in the tool observation
- Scan the observation for every instance of "mp-" followed by digits
- DO NOT synthesize. ONLY copy found codes.
- List: [mp-149, mp-32, mp-2534, mp-804]

STEP 2: Map each material to its mp-code from observation
- Si → mp-149 (found in observation)
- Ge → mp-32 (found in observation)
- GaAs → mp-2534 (found in observation)
- GaN → mp-804 (found in observation)
- Unknown material → ID_NOT_FOUND (not in observation)

STEP 3: Verify every mp-code in my thought block exists in the tool observation
- mp-149: ✓ Present
- mp-32: ✓ Present
- mp-2534: ✓ Present
- mp-804: ✓ Present
- All checks passed. Safe to use these codes in answer.

STEP 4: Identify any materials NOT found in observation
- List: [None - all materials were found]
</thought>
```

**This inventory is your COMMITMENT.** If you list mp-149 in the thought block, you commit to using ONLY mp-149 for that material, not some other code from memory.

---

## RULE #3: NO INFERENCE — ZERO TOLERANCE

These are forbidden:

❌ "Based on my knowledge of materials science, BaTiO3 has mp-code..."
❌ "I believe the mp-code for SiC is..."
❌ "Typical mp-codes for perovskites range from..."
❌ "Following the pattern I see, this should be mp-..."
❌ "It's likely that..."
❌ "I suspect..."
❌ "My training suggests..."

**All of these are hallucination vectors.** Replace them with:

✓ "The observation provides: mp-2895 for BaTiO3"
✓ "No mp-code for [material] appears in the observation"
✓ "ID_NOT_FOUND"

---

## RULE #4: MATERIAL-TO-ID VERIFICATION LOGIC

For each material query:

1. **Find the material name in the observation** (Si, Ge, GaAs, etc.)
2. **Extract the mp-code DIRECTLY adjacent to it**, no interpretation
3. **Copy that exact string**, including any phase information
4. **If the material is not mentioned, output "ID_NOT_FOUND"**

Example observation:
```
[mp-149] Si (Silicon): bandgap 1.20 eV
[mp-32] Ge (Germanium): bandgap 0.67 eV
[mp-2534] GaAs: bandgap 1.43 eV
```

Your mapping:
```
Si → mp-149 ✓ (found adjacent to "Si")
Ge → mp-32 ✓ (found adjacent to "Ge")
GaAs → mp-2534 ✓ (found adjacent to "GaAs")
InP → ID_NOT_FOUND (not mentioned in observation)
```

**You do NOT invent mp-codes for missing materials.** You state ID_NOT_FOUND.

---

## RULE #5: PHASE LABELS ARE MANDATORY

If an observation distinguishes between phases (e.g., cubic vs hexagonal), your answer MUST preserve this:

Observation: "mp-126 (Hexagonal BN), mp-2195 (Cubic BN)"
Your response: "mp-126 (Hexagonal) and mp-2195 (Cubic)"

Observation: "mp-804 (GaN, Cubic phase)"
Your response: "mp-804 (Cubic)"

DO NOT drop phase information. DO NOT merge polymorphs. DO NOT guess which polymorph the user wants—**report all with their phases.**

---

## RULE #6: THE ANTI-HALLUCINATION ANCHOR

Repeat this internal monologue before generating your Final Answer:

> "My memory of Materials Project IDs is a liability. I am prone to synthesizing plausible-sounding codes. I will NOT use any mp-code that I do not see explicitly in the tool observation. If I cannot find a code, I will say ID_NOT_FOUND. I will not guess. I will not infer. I will copy."

---

## RULE #7: MULTI-STEP VERIFICATION BEFORE ANSWERING

Before you write "Final Answer:", verify:

- [ ] Every mp-code I'm about to use was listed in my <thought> block
- [ ] Every mp-code in my <thought> block came from the tool observation, not from my training
- [ ] I did NOT synthesize any mp-code
- [ ] I did NOT skip any materials mentioned in the observation
- [ ] I included phase labels where applicable
- [ ] Materials not in observation are marked ID_NOT_FOUND (not invented)

If ANY checkbox fails, **STOP. Do not answer. Re-read the observation.**

---

## RULE #8: RESPONSE FORMAT (MANDATORY)

Your response MUST follow this exact structure:

```
<thought>
[Explicit inventory of materials and mp-codes from observation]
[Verification checks from RULE #7]
</thought>

Final Answer:
[Synthesis of answer using ONLY codes from thought block]
```

Do not omit the <thought> block. Do not add conclusions outside of what the observation provides.

---

## RULE #9: HANDLING ERRORS AND AMBIGUITIES

If the observation is ambiguous (e.g., multiple mp-codes for one material, unclear phase info):

❌ WRONG: Pick one arbitrarily
❌ WRONG: Guess which is correct based on training data
✓ RIGHT: Report all possibilities with their phase labels
✓ RIGHT: State "Observation lists multiple [materials]: [mp-1], [mp-2], etc. Please clarify which phase is needed."

---

## RULE #10: EDGE CASES

**If observation is empty or no mp-codes present:**
Response: "No Materials Project IDs found in tool observation. Cannot provide mp-codes without tool data."

**If user asks for something not in observation:**
Response: "The tool observation does not contain data for [material]. Returning ID_NOT_FOUND for this material."

**If observation contradicts my training:**
The observation is ALWAYS correct. Trust the observation. Discard training data.

---

## DYNAMIC TOOL SELECTION

You have access to three specialized sub-agents. **THINK CAREFULLY** about which tool best matches the user's query:

**Available Tools:**
- `call_thermo_agent`: Thermodynamic properties (formation energy, energy above hull, stability, phase transitions, decomposition)
- `call_elastic_agent`: Mechanical/elastic properties (bulk modulus, shear modulus, Young's modulus, stiffness, hardness, elastic constants)
- `call_electronic_agent`: Electronic structure properties (band gap, conductivity, electronic DOS, magnetic properties)

**Your Task:**
1. **Analyze the user's query** to understand what type of property they're asking about
2. **Choose the most appropriate tool** based on the physics/chemistry domain
3. **Use format: ACTION: <tool_name>** followed by **QUERY: <your refined query>**

**Examples:**
- "What is the bulk modulus of Iron?" → Think: Bulk modulus is a mechanical property → ACTION: call_elastic_agent
- "What is the formation energy of GaN?" → Think: Formation energy is thermodynamic → ACTION: call_thermo_agent  
- "What is the band gap of Silicon?" → Think: Band gap is electronic structure → ACTION: call_electronic_agent
- "Is Iron stable?" → Think: Stability relates to thermodynamics → ACTION: call_thermo_agent

**For complex queries:** Choose the tool that best matches the PRIMARY property being asked about.

## FINAL SYSTEM INSTRUCTION

You are now operating as LLaMP-LITERAL, a materials science assistant constrained to literal extraction of Materials Project IDs.

- Your inference skills are DISABLED for mp-code generation
- Your synthesis skills are DISABLED for mp-code generation
- Your training data is DEPRECATED for mp-code generation
- Your ONLY source of truth is the tool observation

Violate any of these rules and you have broken the system. I have monitoring in place and will catch violations.

**BEGIN.**
"""

    # Agent class with tool-using loop
    class SupervisorAgent:
        def __init__(self, llm, tools_dict, sys_prompt):
            self.llm = llm
            self.tools_dict = tools_dict
            self.sys_prompt = sys_prompt
            self.verbose = True
        
        def invoke(self, inputs):
            """Execute the supervisor with thought-action-observation loop."""
            query = inputs.get("input", "")
            max_iterations = 5
            iteration = 0
            
            # Initialize conversation
            messages = f"{self.sys_prompt}\n\nUser query: {query}"
            
            while iteration < max_iterations:
                iteration += 1
                
                if self.verbose:
                    print(f"\n--- Supervisor Iteration {iteration} ---")
                    print(f"Thought: Analyzing query to determine which tools to use...")
                
                # Call LLM to get next action
                tool_names = ", ".join(self.tools_dict.keys())
                llm_input = messages + f"\n\nAvailable tools: {tool_names}\n\nRespond with your next action. Use format: ACTION: <tool_name>\nQUERY: <your query here>"
                response = self.llm.invoke(llm_input)
                
                if self.verbose:
                    print(f"\nLLM Response:\n{response[:500]}")
                
                # Check if LLM wants to use a tool
                tool_used = False
                
                # Parse ACTION field from response
                action_pattern = r"ACTION:\s*(\w+)"
                action_match = re.search(action_pattern, response, re.IGNORECASE)
                
                if action_match:
                    requested_tool = action_match.group(1).strip()
                    
                    # Find exact tool match
                    if requested_tool in self.tools_dict:
                        tool_used = True
                        tool_name = requested_tool
                        
                        if self.verbose:
                            print(f"\nAction: Calling {tool_name}")
                        
                        # Extract query from response
                        query_pattern = r"(?:query:|ACTION INPUT:|QUERY:)\s*(.+?)(?:\n|$)"
                        match = re.search(query_pattern, response, re.IGNORECASE | re.MULTILINE)
                        
                        if match:
                            tool_query = match.group(1).strip().strip('"').strip("'")
                        else:
                            tool_query = query
                        
                        if self.verbose:
                            print(f"Query: {tool_query}")
                        
                        # Call tool function - StructuredTool requires .invoke()
                        tool_func = self.tools_dict[tool_name]
                        observation = tool_func.invoke(tool_query)
                        
                        if self.verbose:
                            obs_preview = observation[:300] + "..." if len(observation) > 300 else observation
                            print(f"\nObservation:\n{obs_preview}")
                        
                        # Add to messages for next iteration
                        messages += f"\n\nAction: {tool_name}\nQuery: {tool_query}\nResult: {observation}"
                    else:
                        if self.verbose:
                            print(f"\nError: Requested tool '{requested_tool}' not found. Available: {list(self.tools_dict.keys())}")
                        # Continue without calling any tool
                else:
                    # Fallback: check for tool names mentioned in response (old logic)
                    for tool_name in self.tools_dict.keys():
                        if tool_name in response.lower():
                            tool_used = True
                            
                            if self.verbose:
                                print(f"\nAction: Calling {tool_name} (fallback)")
                            
                            # Extract query from response
                            query_pattern = r"(?:query:|ACTION INPUT:|QUERY:)\s*(.+?)(?:\n|$)"
                            match = re.search(query_pattern, response, re.IGNORECASE | re.MULTILINE)
                            
                            if match:
                                tool_query = match.group(1).strip().strip('"').strip("'")
                            else:
                                tool_query = query
                            
                            if self.verbose:
                                print(f"Query: {tool_query}")
                            
                            # Call tool function - StructuredTool requires .invoke()
                            tool_func = self.tools_dict[tool_name]
                            observation = tool_func.invoke(tool_query)
                            
                            if self.verbose:
                                obs_preview = observation[:300] + "..." if len(observation) > 300 else observation
                                print(f"\nObservation:\n{obs_preview}")
                            
                            # Add to messages for next iteration
                            messages += f"\n\nAction: {tool_name}\nQuery: {tool_query}\nResult: {observation}"
                            break
                
                if not tool_used:
                    # LLM provided direct answer without specifying a tool
                    if self.verbose:
                        print(f"\nFinal Answer:\n{response}")
                    return {"output": response}
                
                # Check if this was sufficient or if we need more data
                if "final answer" in response.lower() or iteration >= max_iterations:
                    # Ask LLM for final synthesis
                    if self.verbose:
                        print(f"\nThought: I have sufficient data. Preparing final answer...")
                    
                    final_prompt = messages + "\n\nBased on all the data retrieved above, provide a clear, coherent final answer to the user's original question. Cite material IDs and units appropriately."
                    final_answer = self.llm.invoke(final_prompt)
                    
                    if self.verbose:
                        print(f"\nFinal Answer:\n{final_answer}")
                    
                    return {"output": final_answer}
            
            # Max iterations reached
            return {"output": "Max iterations reached. Could not find sufficient data."}
    
    # Map tool names to functions for the agent
    tools_dict = {
        "call_thermo_agent": call_thermo_agent,
        "call_elastic_agent": call_elastic_agent,
        "call_electronic_agent": call_electronic_agent,
    }
    
    return SupervisorAgent(llm, tools_dict, system_prompt)


if __name__ == "__main__":
    print("="*80)
    print("Testing LatticeReAct Supervisor Agent with Real LLM Reasoning")
    print("="*80)
    
    supervisor = create_supervisor()
    
    # Test 1: Single property query
    print("\n" + "="*80)
    print("Test 1: Single Property Query")
    print("="*80)
    query1 = "What is the bulk modulus of Iron?"
    print(f"Query: {query1}\n")
    result1 = supervisor.invoke({"input": query1})
    print("\nFinal Answer:")
    print(result1.get("output", result1))
    
    # Test 2: Multi-property query
    print("\n" + "="*80)
    print("Test 2: Multi-Property Query")
    print("="*80)
    query2 = "What is the bandgap and formation energy of GaN?"
    print(f"Query: {query2}\n")
    result2 = supervisor.invoke({"input": query2})
    print("\nFinal Answer:")
    print(result2.get("output", result2))
    print(result2.get("output", result2))

