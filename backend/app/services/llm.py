"""Calls Google Gemini over plain HTTP. Returns None on any failure so callers can fall back."""
import logging

import httpx

from app.config import settings

log = logging.getLogger(__name__)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


async def generate(prompt: str) -> str | None:
    if not settings.gemini_api_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(
                GEMINI_URL.format(model=settings.gemini_model),
                params={"key": settings.gemini_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            res.raise_for_status()
            return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as exc:  # network error, bad key, quota, unexpected response
        log.warning("Gemini call failed, using fallback: %s", exc)
        return None
