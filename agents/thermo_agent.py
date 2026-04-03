"""Thermodynamic properties agent for LatticeReAct."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

from tools.mp_thermo import search_mp_thermo


def create_thermo_agent():
    """
    Create a thermodynamic properties agent.
    
    Returns:
        callable: Agent function that processes thermo queries
    """
    
    class ThermoAgent:
        def __init__(self):
            self.name = "thermo_agent"
            self.description = "Thermodynamic properties agent"
        
        def invoke(self, inputs):
            """Execute thermodynamic query."""
            query = inputs.get("input") or inputs.get("query", "")
            result = search_mp_thermo.invoke({"query": query})
            return {"output": result}
        
        def __call__(self, query):
            """Direct call interface."""
            return self.invoke({"query": query})
    
    return ThermoAgent()


if __name__ == "__main__":
    agent = create_thermo_agent()
    result = agent({"input": "What is the formation energy of GaN?"})
    print(result)

