"""Vector store for resume chunks: ChromaDB when installed, otherwise a small JSON file store.

Both expose the same three methods, so the rest of the app doesn't care which one is used.
"""
import json
import logging
import math
from pathlib import Path

from app.config import settings

log = logging.getLogger(__name__)


class ChromaStore:
    name = "chroma"

    def __init__(self, path: str):
        import chromadb

        self._client = chromadb.PersistentClient(path=path)
        self._get()

    def _get(self):
        return self._client.get_or_create_collection("resume", metadata={"hnsw:space": "cosine"})

    def replace(self, ids, texts, vectors, metadatas):
        self._client.delete_collection("resume")
        self._get().add(ids=ids, documents=texts, embeddings=vectors, metadatas=metadatas)

    def query(self, vector, k):
        col = self._get()
        if col.count() == 0:
            return []
        res = col.query(query_embeddings=[vector], n_results=min(k, col.count()))
        # Chroma returns cosine *distance*; similarity = 1 - distance.
        return [
            {"text": t, "section": m["section"], "score": 1 - d}
            for t, m, d in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
        ]

    def clear(self):
        self._client.delete_collection("resume")
        self._get()


class JsonStore:
    name = "json"

    def __init__(self, path: str):
        self._file = Path(path) / "resume_vectors.json"
        self._file.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        return json.loads(self._file.read_text()) if self._file.exists() else []

    def replace(self, ids, texts, vectors, metadatas):
        rows = [{"text": t, "vector": v, **m} for t, v, m in zip(texts, vectors, metadatas)]
        self._file.write_text(json.dumps(rows))

    def query(self, vector, k):
        def cosine(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
            return dot / norm if norm else 0.0

        scored = [{"text": r["text"], "section": r["section"], "score": cosine(vector, r["vector"])}
                  for r in self._load()]
        return sorted(scored, key=lambda r: r["score"], reverse=True)[:k]

    def clear(self):
        self._file.unlink(missing_ok=True)


def make_store(path: str | None = None):
    path = path or settings.rag_chroma_dir
    try:
        return ChromaStore(path)
    except Exception as exc:  # chromadb missing or broken on this machine
        log.warning("ChromaDB unavailable (%s); using JSON vector store", exc)
        return JsonStore(path)
