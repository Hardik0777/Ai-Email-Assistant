"""Turns text into vectors with Gemini's embedding model."""
import httpx

from app.config import settings
from app.services.llm import LLMUnavailable

BATCH_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:batchEmbedContents"


async def embed_texts(texts: list[str], task: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """task is RETRIEVAL_DOCUMENT for resume chunks and RETRIEVAL_QUERY for the email being answered."""
    if not settings.gemini_api_key:
        raise LLMUnavailable("No GEMINI_API_KEY set")
    model = settings.gemini_embedding_model
    vectors: list[list[float]] = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            for i in range(0, len(texts), 100):  # the API accepts up to 100 texts per call
                batch = texts[i:i + 100]
                res = await client.post(
                    BATCH_URL.format(model=model),
                    headers={"x-goog-api-key": settings.gemini_api_key},
                    json={"requests": [
                        {"model": f"models/{model}", "content": {"parts": [{"text": t}]}, "taskType": task}
                        for t in batch
                    ]},
                )
                res.raise_for_status()
                vectors += [e["values"] for e in res.json()["embeddings"]]
    except httpx.HTTPStatusError as exc:
        raise LLMUnavailable(f"Embedding API returned HTTP {exc.response.status_code}") from exc
    except (httpx.HTTPError, KeyError) as exc:
        raise LLMUnavailable(f"Embedding call failed: {type(exc).__name__}") from exc
    return vectors
