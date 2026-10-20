from __future__ import annotations

import os

from fastapi import FastAPI
from pydantic import BaseModel

from app.retriever import KnowledgeRetriever

try:
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:  # pragma: no cover
    ChatOllama = None
    ChatPromptTemplate = None

app = FastAPI(title="Resilience Alpha - RAG Assistant", version="0.1.0")
retriever = KnowledgeRetriever()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

if ChatOllama is not None:
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Tu es un assistant de sécurité et de gouvernance du projet Resilience Alpha. Réponds uniquement à partir du contexte fourni, en français, en quelques phrases claires. Si le contexte ne suffit pas, dis-le explicitement et repose-toi sur les règles de sécurité de base."
        ),
        ("user", "Contexte :\n{context}\n\nQuestion : {question}\n\nRéponds succinctement, en français, et cite les éléments utiles du contexte."),
    ])
else:
    llm = None
    prompt = None


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "rag-assistant",
        "retrieval": "TF-IDF + cosine similarity",
        "ollama": {
            "base_url": OLLAMA_BASE_URL,
            "model": OLLAMA_MODEL,
            "available": llm is not None,
        },
    }


@app.get("/demo")
def demo() -> dict:
    return {
        "project": "Resilience Alpha",
        "ml_scenario": {
            "name": "transaction anormale",
            "payload": {
                "amount": 6500,
                "currency": "EUR",
                "timestamp": "2026-10-20T02:00:00Z",
                "merchant_id": "ecommerce",
                "frequency": 8,
            },
        },
        "rag_questions": [
            "Quelles sont les mesures de sécurité à mettre en place pour les transactions ?",
            "Que faire en cas de fraude sur des paiements ?",
            "Quels sont les contrôles de gouvernance à respecter ?",
        ],
    }


@app.post("/ask")
def ask(request: AskRequest) -> dict:
    matches = retriever.retrieve(request.question, top_k=3)
    context = "\n\n".join(
        f"- {match['title']}: {match['content']}" for match in matches
    )

    answer = context
    mode = "retrieval-only"

    if llm is not None and prompt is not None:
        try:
            result = llm.invoke(prompt.format(context=context, question=request.question))
            answer = result.content
            mode = "ollama-langchain"
        except Exception:
            answer = context
            mode = "fallback-retrieval"

    return {
        "question": request.question,
        "answer": answer,
        "mode": mode,
        "matches": matches,
    }
