"""Caches AI results so clicking Summarize twice on the same email doesn't call Gemini twice."""
import hashlib
import json

from app.config import settings
from app.schemas import ActionResponse, EmailRequest
from app.services import kv as kv_module
from app.services.metrics import CACHE


def cache_key(action: str, email: EmailRequest, extra: str = "") -> str:
    raw = json.dumps([action, email.subject, email.sender, email.body, email.tone, extra])
    return f"cache:{action}:{hashlib.sha256(raw.encode()).hexdigest()}"


def get(key: str) -> ActionResponse | None:
    raw = kv_module.kv.get(key)
    CACHE.labels(result="hit" if raw else "miss").inc()
    return ActionResponse.model_validate_json(raw) if raw else None


def put(key: str, response: ActionResponse):
    if response.source == "llm":  # never cache fallback answers; retry the AI next time
        kv_module.kv.set(key, response.model_dump_json(), settings.cache_ttl_seconds)
