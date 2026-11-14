"""
Test script to list available Groq models.
"""
import sys
from groq import Groq
from config import get_groq_api_key

def main():
    api_key = get_groq_api_key()

    print("=" * 60)
    print("GROQ AVAILABLE MODELS CHECK")
    print("=" * 60)

    if not api_key or api_key == "gsk_your_groq_api_key_here":
        print("[!] ERROR: Groq API key is missing or not configured.")
        print("    Please set GROQ_API_KEY in your .env file or environment.")
        return 1

    try:
        client = Groq(api_key=api_key)
        models = client.models.list()
        print("\nAvailable Groq Models:")
        for model in models.data:
            print(f" - {model.id} (owned by {model.owned_by})")
        return 0

    except Exception as e:
        err_msg = str(e)
        if api_key and api_key in err_msg:
            err_msg = err_msg.replace(api_key, "[REDACTED_API_KEY]")
        print(f"\n[-] ERROR fetching models from Groq: {err_msg}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
