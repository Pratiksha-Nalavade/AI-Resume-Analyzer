"""
Test script to verify Groq API connectivity and chat completions.
"""
import sys
from groq import Groq
from config import get_groq_api_key, DEFAULT_MODEL

RECOMMENDED_CHAT_MODELS = [
    "llama-3.3-70b-versatile",
    "qwen/qwen3.8-27b",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "openai/gpt-oss-20b",
]

def main():
    api_key = get_groq_api_key()

    print("=" * 60)
    print("GROQ API CONNECTIVITY TEST")
    print("=" * 60)

    if not api_key or api_key == "gsk_your_groq_api_key_here":
        print("[!] ERROR: Groq API key is missing or not configured.")
        print("    Please set GROQ_API_KEY in your .env file or environment.")
        print("    Example: GROQ_API_KEY=gsk_...")
        print("    You can get a free key at: https://console.groq.com/keys")
        return 1

    print("[*] API Key detected: [CONFIGURED - HIDDEN FOR SECURITY]")
    target_model = DEFAULT_MODEL
    print(f"[*] Configured model: {target_model}")

    try:
        client = Groq(api_key=api_key)
        print(f"[*] Sending test prompt to Groq using '{target_model}'...")
        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "user", "content": "Respond with 'Groq API connection successful!' and nothing else."}
                ],
                max_tokens=20,
                temperature=0.2,
            )
        except Exception as model_err:
            err_str = str(model_err).lower()
            if "model_not_found" in err_str or "does not exist" in err_str or "access" in err_str:
                print(f"[!] Note: Model '{target_model}' is not accessible on this account.")
                print("[*] Finding available chat model for your account...")
                account_models = [m.id for m in client.models.list().data]
                fallback_model = None
                for candidate in RECOMMENDED_CHAT_MODELS:
                    if candidate in account_models and candidate != target_model:
                        fallback_model = candidate
                        break
                if not fallback_model:
                    # Pick any non-whisper model
                    non_whisper = [m for m in account_models if not m.startswith("whisper") and "guard" not in m]
                    fallback_model = non_whisper[0] if non_whisper else target_model

                print(f"[*] Testing accessible model '{fallback_model}'...")
                response = client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "user", "content": "Respond with 'Groq API connection successful!' and nothing else."}
                    ],
                    max_tokens=20,
                    temperature=0.2,
                )
                target_model = fallback_model
            else:
                raise model_err

        reply = response.choices[0].message.content.strip()
        print(f"\n[+] SUCCESS! Model '{target_model}' responded from Groq:")
        print(f"    {reply}")
        return 0

    except Exception as e:
        err_msg = str(e)
        if api_key and api_key in err_msg:
            err_msg = err_msg.replace(api_key, "[REDACTED_API_KEY]")
        print(f"\n[-] ERROR connecting to Groq API: {err_msg}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
