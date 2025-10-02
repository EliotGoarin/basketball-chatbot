import os
from dotenv import load_dotenv

load_dotenv()

def _parse_origins(s: str):
    if not s:
        return ["http://localhost:5173"]
    return [x.strip() for x in s.split(",") if x.strip()]

class Settings:
    CORS_ALLOW_ORIGINS = _parse_origins(os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173"))

    # --- Data / retriever ---
    RULES_DIR = os.getenv("RULES_DIR", "backend/data/rules")
    RETRIEVER_MAX_CHARS_PER_CHUNK = int(os.getenv("RETRIEVER_MAX_CHARS_PER_CHUNK", "800"))

    # --- Provider switch (make it available on the instance) ---
    # Options: anthropic | mistral_api | ollama_mistral
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mistral_api").lower()

    # --- Anthropic (optional) ---
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
    CLAUDE_TEMPERATURE = float(os.getenv("CLAUDE_TEMPERATURE", "0.2"))
    CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "800"))

    # --- Mistral API ---
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    MISTRAL_TEMPERATURE = float(os.getenv("MISTRAL_TEMPERATURE", "0.2"))
    MISTRAL_MAX_TOKENS = int(os.getenv("MISTRAL_MAX_TOKENS", "800"))

    # --- Ollama (Mistral local) ---
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

    # --- System prompt ---
    SYSTEM_PROMPT = (
        "You are Chatball, a friendly basketball assistant.\n"
        "- Answer in the user's language.\n"
        "- Prefer grounded facts from the provided CONTEXT.\n"
        "- If the user asks for rules, cite or paraphrase the relevant rule precisely.\n"
        "- If data isn't in context, say so briefly and suggest what you *can* answer.\n"
        "- Format short lists with bullets; be concise.\n"
    )

settings = Settings()
