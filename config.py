import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file with UTF-8 BOM tolerance (utf-8-sig)
load_dotenv(encoding="utf-8-sig")

# Normalize any environment variables that might have been loaded with a BOM prefix
for key in list(os.environ.keys()):
    if key.startswith("\ufeff"):
        clean_key = key.lstrip("\ufeff")
        if clean_key not in os.environ:
            os.environ[clean_key] = os.environ[key]


def _clean_val(val):
    if not val:
        return ""
    val = val.strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1].strip()
    return val


# Groq API configuration
GROQ_API_KEY = _clean_val(os.getenv("GROQ_API_KEY") or os.getenv("\ufeffGROQ_API_KEY"))

# Available models
DEFAULT_MODEL = _clean_val(os.getenv("GROQ_MODEL") or os.getenv("\ufeffGROQ_MODEL")) or "llama-3.3-70b-versatile"
AVAILABLE_MODELS = [
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "mixtral-8x7b-32768",
]


def _has_streamlit_context():
    """Check if code is running inside an active Streamlit runtime."""
    if "streamlit" not in sys.modules:
        return False
    try:
        import streamlit as st
        return hasattr(st, "runtime") and st.runtime.exists()
    except Exception:
        return False


def get_groq_api_key():
    """
    Retrieve the Groq API key from Streamlit session state if present,
    otherwise fallback to environment variable.
    """
    if _has_streamlit_context():
        try:
            import streamlit as st
            if "groq_api_key" in st.session_state and st.session_state["groq_api_key"]:
                return _clean_val(st.session_state["groq_api_key"])
        except Exception:
            pass
    raw = os.getenv("GROQ_API_KEY") or os.getenv("\ufeffGROQ_API_KEY") or ""
    return _clean_val(raw)


def get_selected_model():
    """
    Retrieve selected Groq model from Streamlit session state or fallback to default.
    """
    if _has_streamlit_context():
        try:
            import streamlit as st
            if "selected_model" in st.session_state and st.session_state["selected_model"]:
                return _clean_val(st.session_state["selected_model"])
        except Exception:
            pass
    raw = os.getenv("GROQ_MODEL") or os.getenv("\ufeffGROQ_MODEL") or DEFAULT_MODEL
    return _clean_val(raw) or DEFAULT_MODEL

