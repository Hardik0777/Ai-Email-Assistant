"""Shared test setup: a fake embedder and a throwaway resume store, so tests need no API key."""
import hashlib
import math
import re

import pytest

from app.services.rag import embeddings, resume


def fake_vector(text: str, dims: int = 64) -> list[float]:
    """Bag-of-words hashing: texts sharing words get similar vectors."""
    v = [0.0] * dims
    for word in re.findall(r"[a-z]+", text.lower()):
        v[int(hashlib.md5(word.encode()).hexdigest(), 16) % dims] += 1
    norm = math.sqrt(sum(x * x for x in v)) or 1
    return [x / norm for x in v]


@pytest.fixture(autouse=True)
def isolated_rag(tmp_path, monkeypatch):
    async def fake_embed(texts, task="RETRIEVAL_DOCUMENT"):
        return [fake_vector(t) for t in texts]

    monkeypatch.setattr(embeddings, "embed_texts", fake_embed)
    monkeypatch.setattr(resume, "_rag", resume.ResumeRAG(str(tmp_path / "rag")))
    yield
