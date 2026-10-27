from pydantic import BaseModel, Field


class EmailRequest(BaseModel):
    """What the extension sends for every action."""

    threadId: str = "unknown"
    subject: str = ""
    sender: str = ""
    body: str = Field("", max_length=50_000)
    tone: str | None = "professional"


class ActionResponse(BaseModel):
    """What the backend returns. `source` tells you if real AI or the fallback answered."""

    result: str
    source: str  # "llm" or "fallback"


class UsageEvent(BaseModel):
    action: str
