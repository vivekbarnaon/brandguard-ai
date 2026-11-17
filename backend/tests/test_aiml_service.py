from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from app.schemas.aiml import ComplianceRequest, GuidelineEvidence
from app.services import aiml


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.headers = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, path, json, headers):
        self.headers = headers
        if self.error:
            raise self.error
        return FakeResponse(self.response)


@pytest.mark.asyncio
async def test_call_aiml_sends_internal_token(monkeypatch):
    client = FakeClient({"ok": True})
    monkeypatch.setattr(aiml.httpx, "AsyncClient", lambda **kwargs: client)
    monkeypatch.setattr(
        aiml,
        "get_settings",
        lambda: SimpleNamespace(
            aiml_service_url="http://aiml",
            aiml_internal_token=SimpleNamespace(get_secret_value=lambda: "internal-token"),
        ),
    )

    result = await aiml.call_aiml("/analyze", {"content": "copy"})

    assert result == {"ok": True}
    assert client.headers == {"x-aiml-internal-token": "internal-token"}


@pytest.mark.asyncio
async def test_call_aiml_maps_transport_failure(monkeypatch):
    client = FakeClient(error=httpx.ConnectError("unavailable"))
    monkeypatch.setattr(aiml.httpx, "AsyncClient", lambda **kwargs: client)
    monkeypatch.setattr(
        aiml,
        "get_settings",
        lambda: SimpleNamespace(aiml_service_url="http://aiml", aiml_internal_token=None),
    )

    with pytest.raises(HTTPException) as error:
        await aiml.call_aiml("/analyze", {"content": "copy"})

    assert error.value.status_code == 502


@pytest.mark.asyncio
async def test_analyze_rejects_invalid_contract(monkeypatch):
    async def fake_call(path, payload):
        return {"overall_status": "COMPLIANT"}

    monkeypatch.setattr(aiml, "call_aiml", fake_call)
    request = ComplianceRequest(
        original_content="Copy",
        guideline_context=[
            GuidelineEvidence(chunk_id="chunk-1", guideline_text="Be clear.")
        ],
    )

    with pytest.raises(HTTPException) as error:
        await aiml.analyze(request)

    assert error.value.status_code == 502
