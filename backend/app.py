from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from models.schemas import ChatRequest, ChatResponse
from core.config import settings
from services.retriever import RulesRetriever
from services.llm import ask_claude, LLMNoCreditsError, warmup_llm, stream_ollama_mistral

import json

app = FastAPI(title="Chatball Backend", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = RulesRetriever(
    rules_dir=settings.RULES_DIR,
    max_chunk_chars=settings.RETRIEVER_MAX_CHARS_PER_CHUNK
)

@app.on_event("startup")
def _startup():
    info = warmup_llm()
    print(f"[warmup] {info}")

@app.get("/health")
def health():
    model = (
        settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama_mistral"
        else settings.CLAUDE_MODEL if settings.LLM_PROVIDER == "anthropic"
        else settings.MISTRAL_MODEL
    )
    return {"ok": True, "provider": settings.LLM_PROVIDER, "model": model}

def _build_payload(req: ChatRequest):
    user_last = req.last_user_message()
    if not user_last:
        raise HTTPException(status_code=400, detail="No user message provided.")
    context_chunks = retriever.retrieve(user_last, k=req.top_k or 3)
    context_block = "\n\n".join(f"- {c}" for c in context_chunks) if context_chunks else "- (no local rules found)"
    system_prompt = settings.SYSTEM_PROMPT
    user_payload = f"CONTEXT:\n{context_block}\n\nUSER:\n{user_last}"
    return system_prompt, user_payload, context_chunks

@app.post("/api/chat", response_model=ChatResponse)
def chat_api(req: ChatRequest):
    try:
        system_prompt, user_payload, context_chunks = _build_payload(req)
        answer_text = ask_claude(
            system_prompt=system_prompt,
            user_content=user_payload,
            max_tokens=settings.CLAUDE_MAX_TOKENS,
            temperature=settings.CLAUDE_TEMPERATURE,
        )
        return ChatResponse(answer=answer_text, retrieved=context_chunks)
    except LLMNoCreditsError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    """
    Renvoie un flux NDJSON: chaque ligne = {"delta": "..."} et la dernière {"done": true}.
    Supporté pour LLM_PROVIDER=ollama_mistral.
    """
    if settings.LLM_PROVIDER != "ollama_mistral":
        return JSONResponse(status_code=400, content={"detail": "Streaming is only supported with Ollama provider."})

    try:
        system_prompt, user_payload, _ = _build_payload(req)
    except HTTPException as e:
        raise e

    def ndjson_generator():
        try:
            for delta in stream_ollama_mistral(
                system_prompt=system_prompt,
                user_content=user_payload,
                max_tokens=settings.MISTRAL_MAX_TOKENS,
                temperature=settings.MISTRAL_TEMPERATURE,
                model=settings.OLLAMA_MODEL,
            ):
                yield json.dumps({"delta": delta}, ensure_ascii=False) + "\n"
            yield json.dumps({"done": True}) + "\n"
        except Exception as e:
            # En cas d'erreur pendant le stream, on envoie un message final d'erreur
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(ndjson_generator(), media_type="application/x-ndjson")

# Compat si ton front appelle encore /chat
@app.post("/chat", response_model=ChatResponse)
def chat_compat(req: ChatRequest):
    return chat_api(req)
