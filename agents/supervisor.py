"""Supervisor agent for LatticeReAct - coordinates sub-agents for materials analysis."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')
import re

from agents.thermo_agent import create_thermo_agent
from agents.elastic_agent import create_elastic_agent
from agents.electronic_agent import create_electronic_agent


def create_supervisor():
    """
    Create a hierarchical ReAct supervisor agent that coordinates sub-agents.
    
    The supervisor orchestrates three sub-agents:
    - Thermo agent: Formation energy, decomposition enthalpy, energy above hull
    - Elastic agent: Bulk modulus, shear modulus, stiffness, Young's modulus
    - Electronic agent: Bandgap, electronic structure, Fermi level
    
    CRITICAL: This supervisor uses ZERO LLM reasoning for routing.
    It uses only simple pattern matching to avoid hallucination.
    
    Returns:
        SupervisorAgent: Configured supervisor agent
    """
    
    # Initialize sub-agents
    thermo_agent = create_thermo_agent()
    elastic_agent = create_elastic_agent()
    electronic_agent = create_electronic_agent()
    
    # Create tool definitions as dictionaries
    tools = {
        "thermo_agent": {
            "name": "thermo_agent",
            "func": lambda query: thermo_agent.invoke({"input": query}),
            "keywords": ["formation energy", "energy above hull", "decomposition", "enthalpy", "thermo", "stability", "stable", "lowest energy"],
            "description": "Formation energy, decomposition enthalpy, energy above hull"
        },
        "elastic_agent": {
            "name": "elastic_agent",
            "func": lambda query: elastic_agent.invoke({"input": query}),
            "keywords": ["bulk modulus", "shear modulus", "young modulus", "elastic", "stiffness", "stiff", "modulus", "rigidity", "hardness"],
            "description": "Bulk modulus, shear modulus, stiffness, Young's modulus"
        },
        "electronic_agent": {
            "name": "electronic_agent",
            "func": lambda query: electronic_agent.invoke({"input": query}),
            "keywords": ["bandgap", "band gap", "electronic structure", "fermi", "cbm", "vbm", "gap", "conductor", "semiconductor"],
            "description": "Bandgap, electronic structure, Fermi level"
        },
    }
    
    class SupervisorAgent:
        """
        Hierarchical supervisor agent that routes queries to sub-agents using ZERO THINKING.
        
        CRITICAL ARCHITECTURE:
        ✓ Pattern matching (NO LLM) for tool selection
        ✓ Direct API result formatting (NO LLM synthesis)
        ✓ Result: ZERO hallucination - pure Materials Project data only
        
        The supervisor NEVER uses LLM to:
        - Decide which tools to call (pattern matching only)
        - Interpret or reformat tool results (direct output only)
        
        This eliminates hallucination at the root cause.
        """
        
        def __init__(self, tools):
            self.tools = tools
            self.verbose = True
            self.handle_parsing_errors = True
            self.max_iterations = 8
            self.return_intermediate_steps = False
            self.early_stopping_method = "generate"
            self.max_execution_time = 120
            self.execution_timeout = 120
        
        def _select_tools(self, query):
            """
            Select tools using PURE PATTERN MATCHING - NO LLM REASONING.
            
            This method identifies which property type is being requested and 
            selects only the relevant tools needed for that query.
            
            Strategy:
            1. Check keyword matches in query for each tool
            2. Return ONLY matched tools (do not use all if unclear)
            3. If multiple independent properties requested, use multiple tools
            """
            query_lower = query.lower()

            # Robust property detection for singular/plural phrasing.
            thermo_patterns = [
                r"formation\s+energ(?:y|ies)",
                r"energy\s+above\s+hull",
                r"decomposition",
                r"thermo(?:dynamic)?",
                r"stabil(?:ity|e)",
            ]
            elastic_patterns = [
                r"bulk\s+modulus",
                r"shear\s+modulus",
                r"young'?s?\s+modulus",
                r"elastic",
                r"stiff(?:ness)?",
                r"modulus",
                r"rigidity",
                r"hardness",
            ]
            electronic_patterns = [
                r"band\s*gap",
                r"electronic\s+structure",
                r"fermi",
                r"\bcbm\b",
                r"\bvbm\b",
                r"semiconductor",
                r"conductor",
            ]

            thermo_hit = any(re.search(p, query_lower) for p in thermo_patterns)
            elastic_hit = any(re.search(p, query_lower) for p in elastic_patterns)
            electronic_hit = any(re.search(p, query_lower) for p in electronic_patterns)

            matched_tools = []
            if thermo_hit:
                matched_tools.append("thermo_agent")
            if elastic_hit:
                matched_tools.append("elastic_agent")
            if electronic_hit:
                matched_tools.append("electronic_agent")

            # Conservative fallback for ambiguous phrasing.
            if not matched_tools:
                matched_tools = list(self.tools.keys())

            return matched_tools
        
        def _format_results(self, results):
            """
            Format tool results into clean output - NO LLM INTERPRETATION.
            
            Simply concatenate tool outputs directly without any LLM processing.
            This ensures zero hallucination - what you see is pure API data.
            """
            if not results:
                return "No data found for your query."
            
            # Directly concatenate tool results
            output_lines = []
            for tool_name, result in results.items():
                output_lines.append(str(result))
            
            return '\n'.join(output_lines).strip()
        
        def invoke(self, inputs):
            """
            Execute supervisor agent with tool selection and direct formatting.
            
            Flow:
            1. Select tools using pattern matching (ONLY relevant tools)
            2. Execute selected tools
            3. Format results directly (NO LLM interpretation)
            4. Return raw tool output cleaned of tags
            """
            query = inputs.get("input", "")
            
            if self.verbose:
                print(f"\n[Supervisor] Query: {query}")
            
            # STEP 1: Select tools using PATTERN MATCHING (no LLM reasoning)
            tool_names = self._select_tools(query)
            
            if self.verbose:
                print(f"[Supervisor] Tools selected via pattern matching: {tool_names}")
                
                # Explicit reasoning statement (for debugging)
                query_lower = query.lower()
                if any(kw in query_lower for kw in self.tools["thermo_agent"]["keywords"]):
                    print(f"  → Thermodynamic property detected")
                if any(kw in query_lower for kw in self.tools["elastic_agent"]["keywords"]):
                    print(f"  → Elastic property detected")
                if any(kw in query_lower for kw in self.tools["electronic_agent"]["keywords"]):
                    print(f"  → Electronic property detected")
            
            # STEP 2: Execute selected tools
            results = {}
            iteration = 0
            
            for tool_name in tool_names:
                if iteration >= self.max_iterations:
                    break
                
                tool = self.tools[tool_name]
                if self.verbose:
                    print(f"[Supervisor] Executing {tool_name}...")
                
                try:
                    result = tool["func"](query)
                    if isinstance(result, dict):
                        results[tool_name] = result.get("output", str(result))
                    else:
                        results[tool_name] = result
                    
                    if self.verbose:
                        print(f"[Supervisor] {tool_name} returned {len(str(results[tool_name]))} chars")
                    
                    iteration += 1
                except Exception as e:
                    results[tool_name] = f"No data found for {tool_name.replace('_', ' ')}: {str(e)}"
                    if self.verbose:
                        print(f"[Supervisor] {tool_name} error: {str(e)}")
            
            # STEP 3: Format results directly (NO LLM INTERPRETATION)
            if self.verbose:
                print(f"[Supervisor] Formatting {len(results)} tool results with NO LLM processing...")
            
            final_answer = self._format_results(results)
            
            return {
                "output": final_answer,
                "tool_results": results,
                "tools_used": tool_names
            }
    
    return SupervisorAgent(tools)



if __name__ == "__main__":
    print("="*80)
    print("Testing LatticeReAct Supervisor Agent")
    print("="*80)
    
    supervisor = create_supervisor()
    
    query = "What is the stiffest material with the lowest formation energy in the Si-O system?"
    print(f"\nQuery: {query}\n")
    
    result = supervisor.invoke({"input": query})
    
    print("\n" + "="*80)
    print("Final Result:")
    print("="*80)
    print(result.get("output", result))
    
    print("\n" + "="*80)
    print("Tools Used:")
    print("="*80)
    print(", ".join(result.get("tools_used", [])))

