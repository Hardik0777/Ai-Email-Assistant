"""Resume RAG: ingest a resume, then retrieve the chunks most relevant to an email."""
import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.services.rag import embeddings
from app.services.rag.chunking import chunk_resume
from app.services.rag.extract import extract_text
from app.services.rag.store import make_store


class ResumeRAG:
    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir or settings.rag_chroma_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.store = make_store(str(self.data_dir))
        self._history_file = self.data_dir / "history.json"

    # ---- history / status -------------------------------------------------
    def history(self) -> list[dict]:
        return json.loads(self._history_file.read_text()) if self._history_file.exists() else []

    def status(self) -> dict:
        h = self.history()
        current = h[-1] if h and h[-1].get("active") else None
        return {"has_resume": current is not None, "current": current, "store": self.store.name}

    def _save_history(self, items: list[dict]):
        self._history_file.write_text(json.dumps(items, indent=2))

    # ---- ingest -----------------------------------------------------------
    async def ingest(self, filename: str, data: bytes) -> dict:
        text = extract_text(filename, data)
        chunks = chunk_resume(text, settings.rag_chunk_size, settings.rag_chunk_overlap)
        if not chunks:
            raise ValueError("No text found in the file. Is it a scanned image?")
        # Put the section name in the embedded text so "Projects" chunks match project questions.
        texts = [f"{c.section}: {c.text}" for c in chunks]
        vectors = await embeddings.embed_texts(texts, "RETRIEVAL_DOCUMENT")
        self.store.replace(
            ids=[f"chunk-{i}" for i in range(len(chunks))],
            texts=texts, vectors=vectors,
            metadatas=[{"section": c.section} for c in chunks],
        )
        entry = {
            "filename": filename,
            "chunks": len(chunks),
            "sections": sorted({c.section for c in chunks}),
            "uploaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "active": True,
        }
        history = [{**h, "active": False} for h in self.history()]
        self._save_history(history + [entry])
        return entry

    # ---- retrieve ---------------------------------------------------------
    async def retrieve(self, query: str) -> list[dict]:
        if not settings.rag_enabled or not self.status()["has_resume"]:
            return []
        [vector] = await embeddings.embed_texts([query[:4000]], "RETRIEVAL_QUERY")
        hits = self.store.query(vector, settings.rag_top_k)
        # Relevance filter: drop weak matches so unrelated emails don't get resume details stuffed in.
        return [h for h in hits if h["score"] >= settings.rag_min_score]

    def delete(self):
        self.store.clear()
        self._save_history([{**h, "active": False} for h in self.history()])


_rag: ResumeRAG | None = None


def get_rag() -> ResumeRAG:
    global _rag
    if _rag is None:
        _rag = ResumeRAG()
    return _rag
