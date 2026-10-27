from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

settings.gemini_api_key = ""  # tests always use the offline fallback
client = TestClient(app)

EMAIL = {
    "subject": "Urgent: report due",
    "sender": "Priya <priya@example.com>",
    "body": "Hi Hardik, please send the final project report by Friday. "
            "We also need to schedule a review meeting next week with the team.",
}


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_summarize():
    res = client.post("/api/summarize", json=EMAIL)
    assert res.status_code == 200
    assert res.json()["source"] == "fallback"
    assert res.json()["result"].startswith("•")


def test_reply_uses_sender_name():
    res = client.post("/api/reply", json={**EMAIL, "tone": "friendly"})
    assert "Hi Priya!" in res.json()["result"]


def test_tasks_found():
    res = client.post("/api/tasks", json=EMAIL)
    assert "☐" in res.json()["result"]


def test_classify_urgent():
    res = client.post("/api/classify", json=EMAIL)
    assert res.json()["result"] == "🔴 Urgent"


def test_usage_needs_token():
    assert client.get("/api/users/me/usage").status_code == 401


def test_usage_flow():
    token = client.post("/api/auth/demo-token").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/users/me/usage", json={"action": "summarize"}, headers=headers)
    assert client.get("/api/users/me/usage", headers=headers).json()["summarize"] >= 1
    assert client.delete("/api/users/me", headers=headers).json()["deleted"] is True
