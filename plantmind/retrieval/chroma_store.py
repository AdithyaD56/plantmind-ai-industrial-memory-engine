from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover - optional dependency
    TfidfVectorizer = None
    cosine_similarity = None

try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None


class ChromaMemory:
    def __init__(self, persist_dir: Path):
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None
        self._texts: List[str] = []
        self._metadatas: List[Dict[str, Any]] = []
        self._ids: List[str] = []
        self._vectorizer = TfidfVectorizer(stop_words="english") if TfidfVectorizer is not None else None
        self._matrix = None
        if chromadb is not None:
            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
            self._collection = self._client.get_or_create_collection(name="plantmind_memory")

    def add(self, chunk_id: str, text: str, metadata: Dict[str, Any]) -> None:
        if self._collection is not None:
            self._collection.upsert(ids=[chunk_id], documents=[text], metadatas=[metadata])
        self._ids.append(chunk_id)
        self._texts.append(text)
        self._metadatas.append(metadata)
        self._matrix = None

    def add_many(self, items: Iterable[Dict[str, Any]]) -> None:
        for item in items:
            self.add(item["chunk_id"], item["content"], item.get("metadata", {}))

    def _ensure_matrix(self) -> None:
        if self._matrix is not None or not self._texts or self._vectorizer is None:
            return
        self._matrix = self._vectorizer.fit_transform(self._texts)

    def query(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self._collection is not None:
            result = self._collection.query(query_texts=[text], n_results=top_k)
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]
            ids = result.get("ids", [[]])[0]
            distances = result.get("distances", [[]])[0]
            return [
                {"chunk_id": ids[i], "content": docs[i], "metadata": metas[i], "distance": distances[i]}
                for i in range(len(ids))
            ]
        self._ensure_matrix()
        if self._matrix is not None and self._vectorizer is not None and cosine_similarity is not None:
            query_vec = self._vectorizer.transform([text])
            scores = cosine_similarity(query_vec, self._matrix).ravel()
        else:
            scores = self._simple_scores(text)
        if hasattr(scores, "argsort"):
            order = list(scores.argsort()[::-1][:top_k])
        else:
            order = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)[:top_k]
        results = []
        for idx in order:
            results.append(
                {
                    "chunk_id": self._ids[idx],
                    "content": self._texts[idx],
                    "metadata": self._metadatas[idx],
                    "score": float(scores[idx]),
                }
            )
        return results

    def _simple_scores(self, text: str):
        query_tokens = set(re.findall(r"\w+", text.lower()))
        scores = []
        for stored in self._texts:
            stored_tokens = set(re.findall(r"\w+", stored.lower()))
            union = len(query_tokens | stored_tokens) or 1
            score = len(query_tokens & stored_tokens) / union
            scores.append(score)
        return scores
