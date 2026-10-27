"""Calls Google Gemini over plain HTTP."""
import httpx

from app.config import settings

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class LLMUnavailable(Exception):
    """Raised when there's no API key or the Gemini call fails."""


async def call_gemini(prompt: str) -> str:
    if not settings.gemini_api_key:
        raise LLMUnavailable("No GEMINI_API_KEY set")
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(
                GEMINI_URL.format(model=settings.gemini_model),
                headers={"x-goog-api-key": settings.gemini_api_key},  # header, so the key never appears in logs
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            res.raise_for_status()
            return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except httpx.HTTPStatusError as exc:
        raise LLMUnavailable(f"Gemini returned HTTP {exc.response.status_code}") from exc
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        raise LLMUnavailable(f"Gemini call failed: {type(exc).__name__}") from exc
