"""Elastic properties agent for LatticeReAct - LLM-powered with tool usage."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

import re
from langchain_ollama import OllamaLLM
from langchain_core.tools import tool
from tools.mp_elastic import search_mp_elastic


def create_elastic_agent():
    """
    Create an elastic properties agent powered by Qwen2.5 LLM.
    
    The agent:
    - Uses OllamaLLM for semantic reasoning with temperature=0
    - Has one tool: query_mp_elastic for Materials Project queries
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
    
    # Tool for Materials Project elasticity
    @tool
    def query_mp_elastic(query_str: str) -> str:
        """Query Materials Project for elastic properties."""
        try:
            result = search_mp_elastic.invoke({"query": query_str})
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Wrapper to call the tool (since @tool creates a StructuredTool)
    def call_elastic_tool(query_str):
        return query_mp_elastic.invoke(query_str)
    
    # System prompt for the agent
    system_prompt = """You are an elastic properties materials science expert.
You have access to the Materials Project database via the query_mp_elastic tool.

CRITICAL RULES:
- ONLY query for materials explicitly mentioned in the user's question
- DO NOT invent or assume mp-codes
- Pass the material name/formula exactly as given by the user to the tool
- Let the tool handle the lookup and return whatever it finds

When asked about elastic properties:
1. THINK about what material the user asked for
2. ACTION: Call query_mp_elastic with the exact material name from the user's query
3. OBSERVATION: Read the tool result (may be "no data found" - that's OK)
4. FINAL ANSWER: Report only what was found in the tool result

Always cite material IDs (mp-XXXXX) and units (GPa for modulus).
If the tool returns "no data found", report that honestly."""

    # Agent class with tool-using loop
    class ElasticAgent:
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
                llm_input = messages + f"\n\nRespond with your next action. Use format: ACTION: query_mp_elastic\nQUERY: <your query here>"
                response = self.llm.invoke(llm_input)
                
                if self.verbose:
                    print(f"\nLLM Response:\n{response[:500]}")
                
                # Check if LLM wants to use a tool
                if "query_mp_elastic" in response.lower() or "action:" in response.lower():
                    if self.verbose:
                        print(f"\nAction: Calling query_mp_elastic")
                    
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
                    messages += f"\n\nAction: query_mp_elastic\nQuery: {tool_query}\nResult: {observation}"
                    
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
                        
                        final_prompt = messages + """\n\nBased ONLY on the tool observation data above, provide a final answer. 

CRITICAL RULES:
- ONLY use material IDs (mp-codes) and values that appear in the tool observation
- If a requested material is NOT in the tool observation, state "Material X not found in database"
- DO NOT synthesize, estimate, or use your training knowledge for missing materials  
- DO NOT invent mp-codes or property values
- If multiple materials were requested but only some found, list only the found ones and state which are missing"""
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
    
    return ElasticAgent(llm, system_prompt, call_elastic_tool)


if __name__ == "__main__":
    print("="*80)
    print("Testing Elastic Agent with Real LLM")
    print("="*80)
    
    agent = create_elastic_agent()
    result = agent.invoke({"input": "What is the bulk modulus of Iron?"})
    
    print("\n" + "="*80)
    print("Answer:")
    print("="*80)
    print(result.get("output", result))

