"""Tests the LangChain pipeline with a fake LLM, so no API key or internet is needed."""
from fastapi.testclient import TestClient

from app.main import app
from app.services import llm, prompt_templates

client = TestClient(app)
EMAIL = {"subject": "Team sync", "sender": "Ravi", "body": "Can we meet on Thursday to review the plan?"}


def test_templates_fill_all_fields():
    text = prompt_templates.REPLY.format(subject="S", sender="R", body="B", tone="friendly")
    assert "friendly reply" in text and "Subject: S" in text and "B" in text


def test_chain_uses_llm_output(monkeypatch):
    seen = {}

    async def fake_llm(prompt: str) -> str:
        seen["prompt"] = prompt
        return "Meeting"

    monkeypatch.setattr(llm, "call_gemini", fake_llm)
    res = client.post("/api/classify", json=EMAIL).json()
    assert res == {"result": "🔵 Meeting", "source": "llm"}
    assert "Team sync" in seen["prompt"]


def test_chain_falls_back_when_llm_fails(monkeypatch):
    async def broken_llm(prompt: str) -> str:
        raise llm.LLMUnavailable("down")

    monkeypatch.setattr(llm, "call_gemini", broken_llm)
    res = client.post("/api/summarize", json=EMAIL).json()
    assert res["source"] == "fallback"
