import io

from docx import Document
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services import llm
from app.services.rag.chunking import chunk_resume, split_sections

client = TestClient(app)

RESUME = """Hardik Aggarwal
Projects
AI Email Automation Assistant built with FastAPI, LangChain and Chroma for smart replies.
Distributed payment system with RabbitMQ and Redis idempotency.
Education
B.Tech Electronics and Computer Engineering at Thapar Institute.
Technical Skills
Python, PyTorch, FastAPI, Docker, AWS."""


def make_docx(text: str) -> bytes:
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_sections_detected():
    names = [name for name, _ in split_sections(RESUME)]
    assert names == ["General", "Projects", "Education", "Technical Skills"]


def test_chunks_respect_size_and_overlap():
    long_text = "Projects\n" + " ".join(f"word{i}" for i in range(400))
    chunks = chunk_resume(long_text, size=200, overlap=40)
    assert len(chunks) > 1
    assert all(len(c.text) <= 200 for c in chunks)
    assert chunks[0].text.split()[-1] in chunks[1].text  # overlap carries words forward


def test_upload_status_history_delete():
    assert client.get("/api/resume/status").json()["has_resume"] is False
    res = client.post("/api/resume/upload", files={"file": ("cv.docx", make_docx(RESUME))})
    assert res.status_code == 200, res.text
    assert "Projects" in res.json()["sections"]
    assert client.get("/api/resume/status").json()["has_resume"] is True
    assert len(client.get("/api/resume/history").json()) == 1
    assert client.delete("/api/resume").json()["deleted"] is True
    assert client.get("/api/resume/status").json()["has_resume"] is False


def test_rejects_unsupported_file():
    res = client.post("/api/resume/upload", files={"file": ("cv.txt", b"hello")})
    assert res.status_code == 415


def test_reply_uses_relevant_resume_chunks(monkeypatch):
    seen = {}

    async def fake_llm(prompt: str) -> str:
        seen["prompt"] = prompt
        return "Thanks! I built an AI email assistant with FastAPI and LangChain."

    monkeypatch.setattr(llm, "call_gemini", fake_llm)
    monkeypatch.setattr(settings, "rag_min_score", 0.2)
    client.post("/api/resume/upload", files={"file": ("cv.docx", make_docx(RESUME))})

    email = {"subject": "Your FastAPI LangChain projects",
             "body": "Could you tell us about the AI email assistant you built with FastAPI and LangChain?"}
    res = client.post("/api/reply", json=email).json()
    assert res["rag"] == "used" and res["rag_chunks_used"] >= 1
    assert "Relevant resume details" in seen["prompt"] and "LangChain" in seen["prompt"]


def test_reply_skips_resume_when_irrelevant(monkeypatch):
    async def fake_llm(prompt: str) -> str:
        assert "Relevant resume details" not in prompt
        return "Sure, see you at lunch."

    monkeypatch.setattr(llm, "call_gemini", fake_llm)
    monkeypatch.setattr(settings, "rag_min_score", 0.6)
    client.post("/api/resume/upload", files={"file": ("cv.docx", make_docx(RESUME))})

    res = client.post("/api/reply", json={"subject": "Lunch", "body": "Want to grab lunch tomorrow?"}).json()
    assert res["rag"] == "no_match" and res["rag_chunks_used"] == 0
