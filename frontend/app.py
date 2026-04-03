import streamlit as st
import requests

# Cleanup function for filtering raw agent internals
def clean_answer(text: str) -> str:
    """
    Remove raw agent internals from answer before displaying to user.
    
    Filters out:
    - Agent tags like [THERMO_AGENT], [ELASTIC_AGENT], [ELECTRONIC_AGENT]
    - Separator lines and headers
    - Internal reasoning statements
    - Tool metadata
    """
    lines = text.split('\n')
    cleaned = []
    skip_patterns = [
        '[THERMO_AGENT]',
        '[ELASTIC_AGENT]', 
        '[ELECTRONIC_AGENT]',
        'RESULTS FROM MATERIALS PROJECT DATABASE',
        'Direct Tool Output',
        '================',
        '= RESULTS',
        'Query: Give me',
        'Query: What',
        'Calling: ',
        'Please allow me',
        'Let me call',
        'I need to call',
        'tool result',
        'No interpretation',
        'No hallucination',
        'raw data directly',
        'IMPORTANT:',
    ]
    
    for line in lines:
        should_skip = any(
            pattern in line for pattern in skip_patterns
        )
        if not should_skip:
            cleaned.append(line)
    
    result = '\n'.join(cleaned).strip()
    
    # Remove multiple consecutive blank lines
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    return result

# Page configuration
st.set_page_config(page_title="LatticeReAct", layout="wide")

# Initialize session state for query
if "query" not in st.session_state:
    st.session_state.query = ""

# Callback functions for buttons
def set_query(text):
    st.session_state.query = text

# Title and subtitle
st.title("LatticeReAct")
st.markdown("### hallucination-free materials intelligence")

# How it works expander
with st.expander("How it works"):
    st.markdown("""
    LatticeReAct is a hierarchical agent system that combines:
    - **Specialized Sub-Agents**: Three domain-specific agents for thermodynamic, elastic, and electronic properties
    - **Supervisor Coordination**: An intelligent supervisor agent that routes queries to appropriate sub-agents
    - **Materials Project Integration**: Direct access to verified Materials Project database via API
    - **Caching System**: Fast retrieval of previously answered questions using ChromaDB similarity search
    
    Each query is processed by the supervisor agent, which determines which tools (thermo/elastic/electronic) 
    are needed and synthesizes results into comprehensive, verified answers.
    """)

# Query input section
st.markdown("---")
st.subheader("Ask About Materials Properties")

# Example buttons
st.markdown("##### Quick Examples:")
col1, col2, col3 = st.columns(3)

with col1:
    st.button("Bulk modulus of Iron", on_click=set_query, args=("Bulk modulus of Iron",), key="btn_bulk")

with col2:
    st.button("Bandgap of GaN", on_click=set_query, args=("Bandgap of GaN",), key="btn_bandgap")

with col3:
    st.button("Stiffest material in Si-O system", on_click=set_query, args=("Stiffest material in Si-O system",), key="btn_stiffest")

# Text input
query = st.text_input(
    "Enter your materials science question:",
    placeholder="e.g., What is the bandgap of GaN?",
    value=st.session_state.query
)

# Process query
if st.button("Submit Query", type="primary", key="btn_submit"):
    if not query.strip():
        st.error("Please enter a query!")
    else:
        try:
            with st.spinner("Querying materials database..."):
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"query": query},
                    timeout=120
                )
            
            if response.status_code == 200:
                data = response.json()
                
                # Display answer (cleaned of raw internals)
                st.success("✓ Query processed successfully!")
                cleaned = clean_answer(data['answer'])
                st.markdown(f"**Answer:**\n\n{cleaned}")
                
                # Display source
                source = data.get('source', 'unknown')
                if source == "cache":
                    st.info(f"📦 Result from **Cache** (instant retrieval)")
                else:
                    st.info(f"🔍 Result from **Live API** (newly computed)")
                
                # Display disclaimer
                if data.get('disclaimer'):
                    st.warning(f"**Disclaimer:** {data['disclaimer']}")
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"API Error: {error_detail}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Make sure the FastAPI server is running on http://localhost:8000")
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout. The query took too long to process.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
LatticeReAct • Hierarchical Materials Science Agent System
</div>
""", unsafe_allow_html=True)
