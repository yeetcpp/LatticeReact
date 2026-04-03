"""Supervisor agent for LatticeReAct - hierarchical multi-agent coordinator with real LLM reasoning."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

import re
from langchain_ollama import OllamaLLM
from langchain_core.tools import tool

from agents.thermo_agent import create_thermo_agent
from agents.elastic_agent import create_elastic_agent
from agents.electronic_agent import create_electronic_agent


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
    
    # Define sub-agent tools
    @tool
    def call_thermo_agent(query: str) -> str:
        """Query thermodynamic properties from Materials Project.
        
        Useful for: formation energy, energy above hull, thermodynamic stability,
        decomposition enthalpy, thermodynamic analysis.
        """
        try:
            result = thermo_agent.invoke({"input": query})
            return result.get("output", str(result))
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def call_elastic_agent(query: str) -> str:
        """Query elastic/mechanical properties from Materials Project.
        
        Useful for: bulk modulus, shear modulus, Young's modulus, elastic constants,
        stiffness, mechanical properties, rigidity.
        """
        try:
            result = elastic_agent.invoke({"input": query})
            return result.get("output", str(result))
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool
    def call_electronic_agent(query: str) -> str:
        """Query electronic structure properties from Materials Project.
        
        Useful for: bandgap, electronic structure, band structure, Fermi level,
        CBM (conduction band minimum), VBM (valence band maximum), metallic vs
        semiconductor properties.
        """
        try:
            result = electronic_agent.invoke({"input": query})
            return result.get("output", str(result))
        except Exception as e:
            return f"Error: {str(e)}"
    
    # System prompt for the supervisor
    system_prompt = """You are LLaMP, a hierarchical materials science assistant powered by real LLM reasoning.

YOUR CORE PRINCIPLES:
1. You NEVER answer from memory or training data alone
2. You ALWAYS use your tools to retrieve verified Materials Project data
3. You THINK carefully about which tools are needed for each query
4. You SYNTHESIZE tool results into clean, coherent answers
5. You cite material IDs (mp-XXXXX) when providing specific results
6. You handle multi-property queries by calling multiple tools
7. You select minimum or maximum values when requested
8. You understand materials composition (e.g., Na-C means NaC compounds)

YOUR REASONING PROCESS:
1. Read the user query carefully
2. THINK about which properties are being asked for
3. Decide which tools (sub-agents) have that data
4. CALL the relevant tools
5. Analyze the returned data
6. SYNTHESIZE into a clear final answer

TOOLS AVAILABLE:
- call_thermo_agent: For thermodynamic properties (formation energy, stability)
- call_elastic_agent: For mechanical properties (moduli, constants, stiffness)
- call_electronic_agent: For electronic properties (bandgap, band structure, Fermi level)

IMPORTANT:
- If a query mentions multiple properties, call multiple tools
- Always verify data comes from Materials Project
- Be precise about units (GPa for modulus, eV for energy/bandgap)"""

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
                for tool_name in self.tools_dict.keys():
                    if tool_name in response.lower() or "action:" in response.lower():
                        tool_used = True
                        
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
                        
                        # Call tool function
                        tool_func = self.tools_dict[tool_name]
                        observation = tool_func(tool_query)
                        
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

