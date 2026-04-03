"""Electronic structure agent for LatticeReAct - LLM-powered with tool usage."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

import re
from langchain_ollama import OllamaLLM
from langchain_core.tools import tool
from tools.mp_electronic import search_mp_electronic


def create_electronic_agent():
    """
    Create an electronic properties agent powered by Qwen2.5 LLM.
    
    The agent:
    - Uses OllamaLLM for semantic reasoning with temperature=0
    - Has one tool: query_mp_electronic for Materials Project queries
    - Implements self-correction by reading error messages and retrying
    - Returns synthesized answers, not raw JSON
    
    Returns:
        agent wrapper with invoke method
    """
    
    # Initialize real LLM
    llm = OllamaLLM(
        model="qwen2.5:14b-instruct-q8_0",
        base_url="http://localhost:11434",
        temperature=0,
    )
    
    # Tool for Materials Project electronic structure
    @tool
    def query_mp_electronic(query_str: str) -> str:
        """Query Materials Project for electronic structure properties."""
        try:
            result = search_mp_electronic.invoke({"query": query_str})
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Wrapper to call the tool (since @tool creates a StructuredTool)
    def call_electronic_tool(query_str):
        return query_mp_electronic.invoke(query_str)
    
    # System prompt for the agent
    system_prompt = """You are an electronic structure materials science expert.
You have access to the Materials Project database via the query_mp_electronic tool.

When asked about electronic properties (bandgap, electronic structure, fermi level, CBM, VBM, semiconductor, metallic):
1. THINK about what data you need
2. ACTION: Call query_mp_electronic with the query
3. OBSERVATION: Read the tool result
4. FINAL ANSWER: Synthesize into a clear, natural answer

Always cite material IDs (mp-XXXXX) and units (eV for bandgap).
If the tool returns an error, analyze it and retry with corrected parameters."""

    # Agent class with tool-using loop
    class ElectronicAgent:
        def __init__(self, llm, sys_prompt, tool_func):
            self.llm = llm
            self.sys_prompt = sys_prompt
            self.tool_func = tool_func
            self.verbose = True
        
        def invoke(self, inputs):
            """Execute the agent with thought-action-observation loop."""
            query = inputs.get("input", "")
            max_iterations = 3
            iteration = 0
            
            # Initialize conversation
            messages = f"{self.sys_prompt}\n\nUser query: {query}"
            
            while iteration < max_iterations:
                iteration += 1
                
                if self.verbose:
                    print(f"\n--- Iteration {iteration} ---")
                    print(f"Thought: Thinking about how to answer: {query}")
                
                # Call LLM to get next action
                llm_input = messages + f"\n\nRespond with your next action. Use format: ACTION: query_mp_electronic\nQUERY: <your query here>"
                response = self.llm.invoke(llm_input)
                
                if self.verbose:
                    print(f"\nLLM Response:\n{response[:500]}")
                
                # Check if LLM wants to use a tool
                if "query_mp_electronic" in response.lower() or "action:" in response.lower():
                    if self.verbose:
                        print(f"\nAction: Calling query_mp_electronic")
                    
                    # Extract query from response
                    query_pattern = r"(?:query:|ACTION INPUT:|QUERY:)\s*(.+?)(?:\n|$)"
                    match = re.search(query_pattern, response, re.IGNORECASE | re.MULTILINE)
                    
                    if match:
                        tool_query = match.group(1).strip().strip('"').strip("'")
                    else:
                        tool_query = query
                    
                    if self.verbose:
                        print(f"Query: {tool_query}")
                    
                    # Call tool
                    observation = self.tool_func(tool_query)
                    
                    if self.verbose:
                        obs_preview = observation[:300] + "..." if len(observation) > 300 else observation
                        print(f"\nObservation:\n{obs_preview}")
                    
                    # Add to messages for next iteration
                    messages += f"\n\nAction: query_mp_electronic\nQuery: {tool_query}\nResult: {observation}"
                    
                    # Check if we got data or need to retry
                    if "error" in observation.lower() or "no data" in observation.lower():
                        if iteration < max_iterations:
                            if self.verbose:
                                print(f"\nThought: Got an error, will retry with different parameters...")
                            continue
                    else:
                        # Got data, ask LLM for final answer
                        if self.verbose:
                            print(f"\nThought: I have the data I need. Preparing final answer...")
                        
                        final_prompt = messages + "\n\nBased on the data above, provide a clear final answer to the user's original question."
                        final_answer = self.llm.invoke(final_prompt)
                        
                        if self.verbose:
                            print(f"\nFinal Answer:\n{final_answer}")
                        
                        return {"output": final_answer}
                else:
                    # LLM provided direct answer without tool
                    if self.verbose:
                        print(f"\nFinal Answer:\n{response}")
                    return {"output": response}
            
            # Max iterations reached
            return {"output": "Max iterations reached. Could not find sufficient data."}
    
    return ElectronicAgent(llm, system_prompt, call_electronic_tool)


if __name__ == "__main__":
    print("="*80)
    print("Testing Electronic Agent with Real LLM")
    print("="*80)
    
    agent = create_electronic_agent()
    result = agent.invoke({"input": "What is the bandgap of GaN?"})

