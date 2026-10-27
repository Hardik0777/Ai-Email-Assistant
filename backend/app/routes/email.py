from fastapi import APIRouter, Depends

from app.ratelimit import rate_limit
from app.schemas import ActionResponse, EmailRequest
from app.services import cache, email_ai
from app.services.metrics import AI_RESULTS
from app.services.rag.resume import get_rag

router = APIRouter(prefix="/api", tags=["email"], dependencies=[Depends(rate_limit)])
ACTIONS = {
    "summarize": email_ai.summarize,
    "reply": email_ai.reply,
    "tasks": email_ai.tasks,
    "classify": email_ai.classify,
}


async def _handle(action: str, email: EmailRequest) -> ActionResponse:
    # Replies depend on the resume too, so a new upload must not reuse old cached replies.
    extra = ""
    if action == "reply":
        current = get_rag().status()["current"]
        extra = current["uploaded_at"] if current else ""
    key = cache.cache_key(action, email, extra)

    if cached := cache.get(key):
        return cached
    response = await ACTIONS[action](email)
    AI_RESULTS.labels(action=action, source=response.source).inc()
    cache.put(key, response)
    return response


@router.post("/summarize", response_model=ActionResponse, response_model_exclude_none=True)
async def summarize(email: EmailRequest):
    return await _handle("summarize", email)


@router.post("/reply", response_model=ActionResponse, response_model_exclude_none=True)
async def reply(email: EmailRequest):
    return await _handle("reply", email)


@router.post("/tasks", response_model=ActionResponse, response_model_exclude_none=True)
async def tasks(email: EmailRequest):
    return await _handle("tasks", email)


@router.post("/classify", response_model=ActionResponse, response_model_exclude_none=True)
async def classify(email: EmailRequest):
    return await _handle("classify", email)
