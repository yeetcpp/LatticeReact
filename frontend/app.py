import streamlit as st
import requests
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | frontend.app | %(message)s"
)
logger = logging.getLogger("frontend.app")
logger.info("Streamlit script import started")

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
st.set_page_config(page_title="LatticeReAct", layout="wide", page_icon="⚛️")
logger.info("set_page_config completed")

# Custom CSS for modern design aesthetics
st.markdown("""
<style>
    /* Global font imports */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Hero Section */
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 1.5rem;
        color: #6c757d;
        font-weight: 400;
        margin-bottom: 2.5rem;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        border-radius: 8px;
    }

    /* Buttons Styling */
    div.stButton > button:first-child {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        border-color: #4ECDC4;
        color: #4ECDC4;
    }
    
    /* Input Field Styling */
    div[data-baseweb="input"] {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) inset;
        transition: all 0.3s ease;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #45B7D1;
        box-shadow: 0 0 0 2px rgba(69, 183, 209, 0.2);
    }
    
    /* Primary Submit Button style */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4ECDC4, #45B7D1) !important;
        color: white !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(78, 205, 196, 0.4) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state for query
if "query" not in st.session_state:
    st.session_state.query = ""
logger.info("session_state initialized")

# Callback functions for buttons
def set_query(text):
    st.session_state.query = text

# Title and subtitle
st.markdown('<h1 class="hero-title">LatticeReAct</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">hallucination-free materials intelligence</p>', unsafe_allow_html=True)
logger.info("header rendered")

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
logger.info("how-it-works expander rendered")

# Query input section
st.markdown("---")
st.subheader("Ask About Materials Properties")
logger.info("query section rendered")

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
logger.info("text_input rendered; query length=%d", len(query or ""))

# Process query
if st.button("Submit Query", type="primary", key="btn_submit"):
    logger.info("Submit Query button pressed")
    if not query.strip():
        st.error("Please enter a query!")
        logger.warning("empty query submitted")
    else:
        try:
            logger.info("sending request to backend /query")
            with st.spinner("Querying materials database..."):
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"query": query},
                    timeout=120
                )
            logger.info("backend response received; status=%s", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("backend JSON parsed successfully")
                
                # Display answer (cleaned of raw internals)
                st.success("✓ Query processed successfully!")
                cleaned = clean_answer(data['answer'])
                st.markdown(f"**Answer:**\n\n{cleaned}")
                logger.info("answer rendered; cleaned length=%d", len(cleaned))
                
                # Display source
                source = data.get('source', 'unknown')
                if source == "cache":
                    st.info(f"📦 Result from **Cache** (instant retrieval)")
                else:
                    st.info(f"🔍 Result from **Live API** (newly computed)")
                logger.info("source rendered; source=%s", source)
                
                # Display disclaimer
                if data.get('disclaimer'):
                    st.warning(f"**Disclaimer:** {data['disclaimer']}")
                    logger.info("disclaimer rendered")
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"API Error: {error_detail}")
                logger.error("API returned non-200; detail=%s", error_detail)
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Make sure the FastAPI server is running on http://localhost:8000")
            logger.exception("backend connection error")
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout. The query took too long to process.")
            logger.exception("backend timeout")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.exception("unexpected frontend exception")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
LatticeReAct • Hierarchical Materials Science Agent System
</div>
""", unsafe_allow_html=True)
logger.info("footer rendered; script run completed")
