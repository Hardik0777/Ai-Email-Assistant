"""The four email actions. Each runs its LangChain chain, then falls back to rules if the AI is unavailable."""
import logging

from langchain_core.runnables import Runnable

from app.schemas import ActionResponse, EmailRequest
from app.services import chains, fallback
from app.services.llm import LLMUnavailable
from app.services.rag.resume import get_rag

log = logging.getLogger(__name__)
MAX_BODY = 8000  # keep prompts short and cheap


def _inputs(email: EmailRequest) -> dict:
    return {
        "subject": email.subject,
        "sender": email.sender,
        "body": email.body[:MAX_BODY],
        "tone": email.tone or "professional",
    }


async def _run(chain: Runnable, email: EmailRequest, **extra) -> str | None:
    try:
        return await chain.ainvoke({**_inputs(email), **extra})
    except LLMUnavailable as exc:
        log.warning("Using fallback: %s", exc)
        return None


async def summarize(email: EmailRequest) -> ActionResponse:
    text = await _run(chains.summarize_chain, email)
    return ActionResponse(result=text, source="llm") if text else \
        ActionResponse(result=fallback.summarize(email), source="fallback")


async def reply(email: EmailRequest) -> ActionResponse:
    rag = get_rag()
    hits: list[dict] = []
    rag_state = "no_resume"
    if rag.status()["has_resume"]:
        try:
            hits = await rag.retrieve(f"{email.subject}\n{email.body}")
        except LLMUnavailable as exc:
            log.warning("Resume retrieval skipped: %s", exc)
        rag_state = "used" if hits else "no_match"

    if hits:
        context = "\n\n".join(h["text"] for h in hits)
        text = await _run(chains.reply_with_resume_chain, email, resume_context=context)
    else:
        text = await _run(chains.reply_chain, email)

    if not text:
        return ActionResponse(result=fallback.reply(email), source="fallback")
    return ActionResponse(result=text, source="llm", rag=rag_state, rag_chunks_used=len(hits))


async def tasks(email: EmailRequest) -> ActionResponse:
    text = await _run(chains.tasks_chain, email)
    return ActionResponse(result=text, source="llm") if text else \
        ActionResponse(result=fallback.tasks(email), source="fallback")


async def classify(email: EmailRequest) -> ActionResponse:
    text = await _run(chains.classify_chain, email)
    label = next((c for c in fallback.CATEGORY_ICONS if text and c.lower() in text.lower()), None)
    source = "llm" if label else "fallback"
    label = label or fallback.classify_label(email)
    return ActionResponse(result=f"{fallback.CATEGORY_ICONS[label]} {label}", source=source)
