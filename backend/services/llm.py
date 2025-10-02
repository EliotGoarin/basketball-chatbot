from typing import Optional, Dict, Any, List, Iterator
import time, json
import requests
from requests.exceptions import ReadTimeout, ConnectTimeout
from anthropic import Anthropic
from core.config import settings

class LLMNoCreditsError(RuntimeError): ...
class LLMTimeoutError(RuntimeError): ...

# ===== Anthropic (non-stream, conservé pour bascule éventuelle) =====
_anthropic_client: Optional[Anthropic] = None
def _anthropic() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set.")
        _anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client

def _ask_anthropic(system_prompt: str, user_content: str, max_tokens: int, temperature: float, model: str) -> str:
    client = _anthropic()
    try:
        resp = client.messages.create(
            model=model, max_tokens=max_tokens, temperature=temperature, system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_content}]}],
        )
    except Exception as e:
        msg = str(e).lower()
        if any(s in msg for s in ["credit balance","payment required","insufficient credits","billing"]):
            raise LLMNoCreditsError("Anthropic billing: insufficient credits.")
        raise
    out: List[str] = []
    for block in resp.content:
        if block.type == "text":
            out.append(block.text)
    return "\n".join(out).strip()

# ===== Mistral API (non-stream) =====
_MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
def _ask_mistral_api(system_prompt: str, user_content: str, max_tokens: int, temperature: float, model: str) -> str:
    if not settings.MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is not set.")
    headers = {"Authorization": f"Bearer {settings.MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        r = requests.post(_MISTRAL_URL, json=payload, headers=headers, timeout=90)
    except (ReadTimeout, ConnectTimeout):
        raise LLMTimeoutError("Mistral API timeout.")
    if r.status_code in (401, 402):
        raise LLMNoCreditsError(f"Mistral API billing/auth: {r.status_code}")
    if r.status_code >= 400:
        try: err = r.json()
        except Exception: err = {"error": r.text}
        msg = str(err)
        if any(s in msg.lower() for s in ["insufficient","credit","billing","payment","quota"]):
            raise LLMNoCreditsError(f"Mistral API billing/credits error: {msg}")
        raise RuntimeError(f"Mistral API error {r.status_code}: {msg}")
    data = r.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        raise RuntimeError(f"Unexpected Mistral response format: {data}")

# ===== Ollama (local) non-stream =====
def _ask_ollama_mistral(system_prompt: str, user_content: str, max_tokens: int, temperature: float, model: str) -> str:
    url = settings.OLLAMA_URL.rstrip("/") + "/api/generate"
    prompt = f"{system_prompt}\n\nUSER:\n{user_content}"
    payload = {"model": model, "prompt": prompt, "options": {"temperature": temperature, "num_predict": max_tokens}, "stream": False}
    last_err = None
    for _ in range(2):
        try:
            r = requests.post(url, json=payload, timeout=120)
            if r.status_code >= 400:
                try: err = r.json()
                except Exception: err = {"error": r.text}
                raise RuntimeError(f"Ollama error {r.status_code}: {err}")
            data = r.json()
            if "response" not in data:
                raise RuntimeError(f"Unexpected Ollama response: {data}")
            return str(data["response"]).strip()
        except (ReadTimeout, ConnectTimeout):
            last_err = LLMTimeoutError("Ollama took too long to respond (timeout)."); time.sleep(1.5)
        except Exception as e:
            last_err = e; time.sleep(1.5)
    if isinstance(last_err, (ReadTimeout, ConnectTimeout, LLMTimeoutError)):
        raise LLMTimeoutError("Ollama timed out twice. Try fewer tokens or a smaller model.")
    raise last_err or RuntimeError("Unknown Ollama error")

# ===== Ollama (local) STREAM =====
def stream_ollama_mistral(system_prompt: str, user_content: str, max_tokens: int, temperature: float, model: str) -> Iterator[str]:
    """
    Génère des deltas de texte via /api/generate stream=True.
    Renvoie des *chunks* de texte (pas du JSON) — le endpoint FastAPI emballera en NDJSON.
    """
    url = settings.OLLAMA_URL.rstrip("/") + "/api/generate"
    prompt = f"{system_prompt}\n\nUSER:\n{user_content}"
    payload = {"model": model, "prompt": prompt, "options": {"temperature": temperature, "num_predict": max_tokens}, "stream": True}

    with requests.post(url, json=payload, stream=True, timeout=120) as r:
        if r.status_code >= 400:
            try: err = r.json()
            except Exception: err = {"error": r.text}
            raise RuntimeError(f"Ollama error {r.status_code}: {err}")
        # Chaque ligne est un JSON avec "response": "...", et à la fin "done": true
        buffer = b""
        for raw in r.iter_lines(decode_unicode=False):
            if raw is None:
                continue
            line = raw.decode("utf-8").strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                # Ligne partielle : on ignore (ou on pourrait bufferiser)
                continue
            if "response" in obj and obj["response"]:
                yield str(obj["response"])
            if obj.get("done"):
                break

# ===== Entrées publiques =====
def ask_claude(system_prompt: str, user_content: str, max_tokens: int = 800, temperature: float = 0.2, model: str = "") -> str:
    prov = settings.LLM_PROVIDER
    if prov == "mistral_api":
        return _ask_mistral_api(system_prompt, user_content, settings.MISTRAL_MAX_TOKENS, settings.MISTRAL_TEMPERATURE, settings.MISTRAL_MODEL)
    elif prov == "ollama_mistral":
        return _ask_ollama_mistral(system_prompt, user_content, settings.MISTRAL_MAX_TOKENS, settings.MISTRAL_TEMPERATURE, settings.OLLAMA_MODEL)
    elif prov == "anthropic":
        return _ask_anthropic(system_prompt, user_content, settings.CLAUDE_MAX_TOKENS, settings.CLAUDE_TEMPERATURE, settings.CLAUDE_MODEL)
    else:
        raise RuntimeError(f"Unknown LLM_PROVIDER: {prov}")

def warmup_llm() -> str:
    if settings.LLM_PROVIDER == "ollama_mistral":
        try:
            # Warm courte pour charger le modèle
            _ = _ask_ollama_mistral("You are a noop.", "Say: ok", 8, 0.0, settings.OLLAMA_MODEL)
            return "ollama warmup ok"
        except Exception as e:
            return f"warmup failed: {e}"
    return "warmup not needed"
