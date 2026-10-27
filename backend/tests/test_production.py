import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import kv, llm

client = TestClient(app)
EMAIL = {"subject": "Weekly report", "body": "Please send the weekly report by Friday."}


def _counting_llm(monkeypatch):
    calls = {"n": 0}

    async def fake(prompt: str) -> str:
        calls["n"] += 1
        return "• **Action Required:** send the report by Friday."

    monkeypatch.setattr(llm, "call_gemini", fake)
    return calls


def test_second_identical_request_is_cached(monkeypatch):
    calls = _counting_llm(monkeypatch)
    first = client.post("/api/summarize", json=EMAIL).json()
    second = client.post("/api/summarize", json=EMAIL).json()
    assert first == second and calls["n"] == 1


def test_fallback_answers_are_not_cached(monkeypatch):
    async def broken(prompt):
        raise llm.LLMUnavailable("down")

    monkeypatch.setattr(llm, "call_gemini", broken)
    client.post("/api/summarize", json=EMAIL)
    calls = _counting_llm(monkeypatch)
    assert client.post("/api/summarize", json=EMAIL).json()["source"] == "llm"
    assert calls["n"] == 1


def test_rate_limit_returns_429(monkeypatch):
    _counting_llm(monkeypatch)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 3)
    codes = [client.post("/api/classify", json=EMAIL).status_code for _ in range(5)]
    assert codes == [200, 200, 200, 429, 429]


def test_works_with_real_redis_protocol(monkeypatch):
    fakeredis = pytest.importorskip("fakeredis")  # dev-only dependency
    calls = _counting_llm(monkeypatch)
    monkeypatch.setattr(kv, "kv", kv.RedisKV(fakeredis.FakeRedis(decode_responses=True)))
    client.post("/api/tasks", json=EMAIL)
    client.post("/api/tasks", json=EMAIL)
    assert calls["n"] == 1


def test_metrics_endpoint(monkeypatch):
    _counting_llm(monkeypatch)
    client.post("/api/summarize", json=EMAIL)
    body = client.get("/metrics").text
    assert "http_requests_total" in body and 'path="/api/summarize"' in body
    assert "ai_results_total" in body


def test_health_reports_components():
    data = client.get("/health").json()
    assert data["cache"] == "memory" and data["vector_store"] in {"chroma", "json"}
