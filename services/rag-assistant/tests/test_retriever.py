import sys
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

from app.retriever import KnowledgeRetriever


def test_retriever_returns_relevant_matches():
    retriever = KnowledgeRetriever()
    matches = retriever.retrieve("sécurité du service de paiement", top_k=2)
    assert len(matches) > 0
    assert matches[0]["title"]


def test_retriever_handles_transaction_fraud_question():
    retriever = KnowledgeRetriever()
    matches = retriever.retrieve("fraude sur les transactions de paiement", top_k=3)
    assert len(matches) > 0
    assert any("transaction" in match["title"].lower() or "fraude" in match["title"].lower() for match in matches)
