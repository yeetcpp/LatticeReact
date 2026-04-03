import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Configuration Constants
# ============================================================================

# Materials Project API Key
MP_API_KEY = os.getenv("MP_API_KEY")

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME")

# ChromaDB Configuration
CHROMA_PERSIST_PATH = os.getenv("CHROMA_PERSIST_PATH", "./cache/chromadb")

# Similarity Threshold for Vector Search
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.2"))


# ============================================================================
# Configuration Validation
# ============================================================================

def validate_config() -> None:
    """
    Validates that all required configuration parameters are present.
    
    Raises:
        ValueError: If any required configuration key is missing.
    """
    required_keys = {
        "MP_API_KEY": MP_API_KEY,
        "MODEL_NAME": MODEL_NAME,
        "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
    }
    
    missing_keys = [key for key, value in required_keys.items() if value is None]
    
    if missing_keys:
        raise ValueError(
            f"Missing required configuration keys: {', '.join(missing_keys)}. "
            f"Please ensure these are set in your .env file."
        )


if __name__ == "__main__":
    validate_config()
    print("✓ Configuration validated successfully")
    print(f"  MP_API_KEY: {'*' * (len(MP_API_KEY) - 4) + MP_API_KEY[-4:]}")
    print(f"  OLLAMA_BASE_URL: {OLLAMA_BASE_URL}")
    print(f"  MODEL_NAME: {MODEL_NAME}")
    print(f"  CHROMA_PERSIST_PATH: {CHROMA_PERSIST_PATH}")
    print(f"  SIMILARITY_THRESHOLD: {SIMILARITY_THRESHOLD}")
