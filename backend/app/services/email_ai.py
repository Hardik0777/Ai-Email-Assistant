"""The four email actions. Each runs its LangChain chain, then falls back to rules if the AI is unavailable."""
import logging

from langchain_core.runnables import Runnable

from app.schemas import ActionResponse, EmailRequest
from app.services import chains, fallback
from app.services.llm import LLMUnavailable

log = logging.getLogger(__name__)
MAX_BODY = 8000  # keep prompts short and cheap


def _inputs(email: EmailRequest) -> dict:
    return {
        "subject": email.subject,
        "sender": email.sender,
        "body": email.body[:MAX_BODY],
        "tone": email.tone or "professional",
    }


async def _run(chain: Runnable, email: EmailRequest) -> str | None:
    try:
        return await chain.ainvoke(_inputs(email))
    except LLMUnavailable as exc:
        log.warning("Using fallback: %s", exc)
        return None


async def summarize(email: EmailRequest) -> ActionResponse:
    text = await _run(chains.summarize_chain, email)
    return ActionResponse(result=text, source="llm") if text else \
        ActionResponse(result=fallback.summarize(email), source="fallback")


async def reply(email: EmailRequest) -> ActionResponse:
    text = await _run(chains.reply_chain, email)
    return ActionResponse(result=text, source="llm") if text else \
        ActionResponse(result=fallback.reply(email), source="fallback")


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
