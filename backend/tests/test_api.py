"""Runs against SQLite with the Sarvam HTTP call mocked, so no network/Postgres needed."""
import os

os.environ.update(
    SARVAM_API_KEY="test-key",
    SARVAM_ORG_ID="org",
    SARVAM_WORKSPACE_ID="ws",
    SARVAM_APP_ID="app123",
    SARVAM_APP_VERSION="3",
    SARVAM_CONNECTION_ID="conn123",
    SARVAM_AGENT_PHONE_NUMBER="+918040000000",
    PUBLIC_BASE_URL="https://example.ngrok.app",
    WEBHOOK_TOKEN="secret",
    DATABASE_URL="sqlite:///./test.db",
    CORS_ORIGINS="http://localhost:3000",
)

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import db as dbmod  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    if os.path.exists("test.db"):
        os.remove("test.db")
    dbmod._engine = None
    dbmod._SessionLocal = None
    yield
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def client(monkeypatch):
    captured = {}

    async def fake_post(self, url, json=None, headers=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return httpx.Response(200, json={"attempt_id": "att-1"})

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    with TestClient(app) as c:
        c.captured = captured
        yield c


def test_create_lead_places_call(client):
    r = client.post(
        "/leads",
        json={"name": "Amit", "phone": "98765 43210", "preferred_language": "Hindi", "consent": True},
    )
    assert r.status_code == 201, r.text
    assert r.json()["attempt_id"] == "att-1"

    cap = client.captured
    assert cap["url"] == "https://apps.sarvam.ai/api/outbounds/v1/orgs/org/workspaces/ws/outbounds"
    assert cap["headers"]["X-API-Key"] == "test-key"
    body = cap["json"]
    assert body["user_config"] == {"user_phone_number": "+919876543210"}
    assert body["app_config"]["app_id"] == "app123"
    assert body["app_config"]["app_version"] == 3
    assert body["app_config"]["connection_config"] == {
        "connection_id": "conn123",
        "agent_phone_number": "+918040000000",
    }
    assert body["app_config"]["app_overrides"]["initial_language_name"] == "Hindi"
    assert body["app_config"]["agent_variables"] == {"user_name": "Amit", "lead_id": r.json()["lead_id"]}
    assert body["webhook_config"]["url"] == "https://example.ngrok.app/webhooks/sarvam?token=secret"
    assert body["webhook_config"]["metadata"]["lead_id"] == r.json()["lead_id"]


def test_consent_required(client):
    r = client.post("/leads", json={"name": "A", "phone": "9876543210", "consent": False})
    assert r.status_code == 422


def test_webhook_updates_attempt(client):
    lead = client.post("/leads", json={"name": "Amit", "phone": "9876543210", "consent": True}).json()
    payload = {
        "attempt_id": "att-1",
        "status": "connected",
        "channel_info": {"channel_type": "v2v", "channel_provider": "exotel", "agent_phone_number": "+918040000000"},
        "duration": 16.83,
        "interaction_id": "20250920/abc",
        "failure_reason": None,
        "final_agent_variables": {"vehicle": "Swift 2019", "budget": "8000"},
        "webhook_config": {"url": "x", "metadata": {"lead_id": lead["lead_id"]}},
        "interaction_transcript": [{"role": "agent", "en_text": "Hello"}, {"role": "user", "en_text": "Hi"}],
    }
    assert client.post("/webhooks/sarvam?token=wrong", json=payload).status_code == 401
    r = client.post("/webhooks/sarvam?token=secret", json=payload)
    assert r.status_code == 200 and r.json()["stored"] is True

    detail = client.get(f"/leads/{lead['lead_id']}").json()
    call = detail["calls"][0]
    assert call["status"] == "connected"
    assert call["final_agent_variables"]["vehicle"] == "Swift 2019"
    assert len(call["transcript"]) == 2


def test_webhook_no_answer(client):
    lead = client.post("/leads", json={"name": "Amit", "phone": "9876543210", "consent": True}).json()
    payload = {
        "attempt_id": "att-1",
        "status": "no_answer",
        "channel_info": {"channel_type": "v2v", "channel_provider": "exotel", "agent_phone_number": "+918040000000"},
        "duration": None, "interaction_id": None, "failure_reason": None,
        "final_agent_variables": None, "webhook_config": {"url": "x", "metadata": None},
        "interaction_transcript": None,
    }
    assert client.post("/webhooks/sarvam?token=secret", json=payload).status_code == 200
    assert client.get(f"/leads/{lead['lead_id']}").json()["calls"][0]["status"] == "no_answer"
