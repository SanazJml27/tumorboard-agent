"""
Retrieval layer used to attach supporting citations to agent rationale text.

This is TF-IDF/cosine-similarity based by default (offline, no external
model download). It exists mainly to ground the narrative text agents
produce in a specific, citable knowledge base entry -- the *decisions*
themselves are made by the deterministic logic in oncology_knowledge.py,
not by retrieval score.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"


class KnowledgeBase:
    def __init__(self, data_path: Path = DATA_PATH):
        with open(data_path, "r", encoding="utf-8") as f:
            self._records = json.load(f)
        self._by_id: Dict[str, dict] = {r["kb_id"]: r for r in self._records}
        self._texts = [r["text"] for r in self._records]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._doc_matrix = self._vectorizer.fit_transform(self._texts)

    def get(self, kb_id: str) -> dict | None:
        return self._by_id.get(kb_id)

    def retrieve(self, query: str, top_k: int = 2) -> List[dict]:
        query_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._doc_matrix)[0]
        ranked = sorted(enumerate(sims), key=lambda p: p[1], reverse=True)[:top_k]
        return [
            {**self._records[idx], "score": float(round(score, 4))}
            for idx, score in ranked
            if score > 0
        ]
