"""Rule-based answers used when no AI key is set or the AI call fails."""
import re

from app.schemas import EmailRequest

CATEGORY_ICONS = {
    "Urgent": "🔴", "Opportunity": "🟣", "Meeting": "🔵", "Promotional": "⚪", "Normal": "🟢",
}


def _sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text)
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if len(s) > 20]


def summarize(email: EmailRequest) -> str:
    top = _sentences(email.body)[:3]
    return "\n".join(f"• {s}" for s in top) or "Email is too short to summarize."


def reply(email: EmailRequest) -> str:
    name = re.split(r"[<@]", email.sender)[0].strip() or "there"
    opener = f"Hi {name}!" if email.tone == "friendly" else f"Hello {name},"
    return (
        f"{opener}\n\nThank you for your email regarding \"{email.subject}\". "
        "I'll review it and get back to you shortly.\n\nBest regards"
    )


def tasks(email: EmailRequest) -> str:
    pattern = re.compile(
        r"\b(please|kindly|need to|must|should|deadline|due|by (monday|tuesday|wednesday|"
        r"thursday|friday|tomorrow|today|eod))\b",
        re.IGNORECASE,
    )
    found = [s for s in _sentences(email.body) if pattern.search(s)]
    return "\n".join(f"☐ {s}" for s in found) or "No tasks or deadlines found."


def classify_label(email: EmailRequest) -> str:
    text = f"{email.subject} {email.body}".lower()
    if re.search(r"urgent|asap|immediately|deadline|today", text):
        return "Urgent"
    if re.search(r"interview|offer|opportunity|hiring|position", text):
        return "Opportunity"
    if re.search(r"unsubscribe|newsletter|sale|discount", text):
        return "Promotional"
    if re.search(r"meeting|schedule|call|invite", text):
        return "Meeting"
    return "Normal"
