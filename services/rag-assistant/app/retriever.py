from __future__ import annotations

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeRetriever:
    def __init__(self, knowledge_path: str | None = None):
        self.knowledge_path = (
            Path(knowledge_path) if knowledge_path else Path(__file__).resolve().parents[1] / "data" / "knowledge_base.json"
        )
        self.documents = self._load_documents()
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform([doc["content"] for doc in self.documents])

    def _load_documents(self) -> list[dict]:
        if not self.knowledge_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {self.knowledge_path}")

        with self.knowledge_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def retrieve(self, question: str, top_k: int = 3) -> list[dict]:
        question_vector = self.vectorizer.transform([question])
        scores = cosine_similarity(question_vector, self.matrix).flatten()
        ranked_indexes = scores.argsort()[::-1][:top_k]

        matches = []
        for idx in ranked_indexes:
            matches.append({
                "title": self.documents[idx]["title"],
                "content": self.documents[idx]["content"],
                "score": round(float(scores[idx]), 4),
            })
        return matches
