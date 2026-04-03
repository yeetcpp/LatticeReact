"""Elastic properties agent for LatticeReAct."""
import sys
sys.path.insert(0, '/home/letushack/Documents/TempFileRith/LatticeReAct')

from tools.mp_elastic import search_mp_elastic


def create_elastic_agent():
    """
    Create an elastic properties agent.
    
    Returns:
        callable: Agent function that processes elastic queries
    """
    
    class ElasticAgent:
        def __init__(self):
            self.name = "elastic_agent"
            self.description = "Elastic properties agent"
        
        def invoke(self, inputs):
            """Execute elastic properties query."""
            query = inputs.get("input") or inputs.get("query", "")
            result = search_mp_elastic.invoke({"query": query})
            return {"output": result}
        
        def __call__(self, query):
            """Direct call interface."""
            return self.invoke({"query": query})
    
    return ElasticAgent()


if __name__ == "__main__":
    agent = create_elastic_agent()
    result = agent({"input": "What is the bulk modulus of Iron?"})
    print(result)

