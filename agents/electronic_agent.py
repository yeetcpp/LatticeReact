"""Electronic structure agent for LatticeReAct."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

from tools.mp_electronic import search_mp_electronic


def create_electronic_agent():
    """
    Create an electronic structure agent.
    
    Returns:
        callable: Agent function that processes electronic queries
    """
    
    class ElectronicAgent:
        def __init__(self):
            self.name = "electronic_agent"
            self.description = "Electronic structure agent"
        
        def invoke(self, inputs):
            """Execute electronic structure query."""
            query = inputs.get("input") or inputs.get("query", "")
            result = search_mp_electronic.invoke({"query": query})
            return {"output": result}
        
        def __call__(self, query):
            """Direct call interface."""
            return self.invoke({"query": query})
    
    return ElectronicAgent()


if __name__ == "__main__":
    agent = create_electronic_agent()
    result = agent({"input": "What is the bandgap of GaN?"})
    print(result)

