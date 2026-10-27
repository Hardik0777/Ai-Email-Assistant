"""The four email actions. Each tries the LLM first, then the rule-based fallback."""
from app.schemas import ActionResponse, EmailRequest
from app.services import fallback, llm, prompts

MAX_BODY = 8000  # keep prompts short and cheap


def _fill(template: str, email: EmailRequest) -> str:
    return template.format(
        subject=email.subject, sender=email.sender,
        body=email.body[:MAX_BODY], tone=email.tone or "professional",
    )


async def summarize(email: EmailRequest) -> ActionResponse:
    text = await llm.generate(_fill(prompts.SUMMARIZE, email))
    return ActionResponse(result=text, source="llm") if text else \
        ActionResponse(result=fallback.summarize(email), source="fallback")


async def reply(email: EmailRequest) -> ActionResponse:
    text = await llm.generate(_fill(prompts.REPLY, email))
    return ActionResponse(result=text, source="llm") if text else \
        ActionResponse(result=fallback.reply(email), source="fallback")


async def tasks(email: EmailRequest) -> ActionResponse:
    text = await llm.generate(_fill(prompts.TASKS, email))
    return ActionResponse(result=text, source="llm") if text else \
        ActionResponse(result=fallback.tasks(email), source="fallback")


async def classify(email: EmailRequest) -> ActionResponse:
    text = await llm.generate(_fill(prompts.CLASSIFY, email))
    label = next((c for c in fallback.CATEGORY_ICONS if text and c.lower() in text.lower()), None)
    source = "llm" if label else "fallback"
    label = label or fallback.classify_label(email)
    return ActionResponse(result=f"{fallback.CATEGORY_ICONS[label]} {label}", source=source)
