from types import SimpleNamespace

import httpx
import pytest

from app.services import storage


class FakeResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        return None


class FakeAsyncClient:
    def __init__(self, **kwargs):
        del kwargs
        self.request_url = None
        self.request_headers = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        del exc_type, exc, traceback
        return False

    async def delete(self, url, headers):
        self.request_url = url
        self.request_headers = headers
        return FakeResponse()


class MissingResponse:
    status_code = 404

    def raise_for_status(self) -> None:
        raise AssertionError("A missing storage object should be treated as deleted.")


@pytest.mark.asyncio
async def test_delete_private_uses_supabase_object_delete(monkeypatch):
    client = FakeAsyncClient()
    monkeypatch.setattr(storage.httpx, "AsyncClient", lambda **kwargs: client)
    monkeypatch.setattr(
        storage,
        "get_settings",
        lambda: SimpleNamespace(
            supabase_url="https://example.supabase.co/",
            storage_bucket="brand-guidelines",
            supabase_secret_key=SimpleNamespace(get_secret_value=lambda: "secret"),
        ),
    )

    await storage.delete_private("org-1/document-1/Brand Guide.pdf")

    assert client.request_url == (
        "https://example.supabase.co/storage/v1/object/"
        "brand-guidelines/org-1/document-1/Brand%20Guide.pdf"
    )
    assert client.request_headers["Authorization"] == "Bearer secret"


@pytest.mark.asyncio
async def test_delete_private_treats_missing_object_as_success(monkeypatch):
    class MissingAsyncClient(FakeAsyncClient):
        async def delete(self, url, headers):
            del url, headers
            return MissingResponse()

    client = MissingAsyncClient()
    monkeypatch.setattr(storage.httpx, "AsyncClient", lambda **kwargs: client)
    monkeypatch.setattr(
        storage,
        "get_settings",
        lambda: SimpleNamespace(
            supabase_url="https://example.supabase.co",
            storage_bucket="brand-guidelines",
            supabase_secret_key=SimpleNamespace(get_secret_value=lambda: "secret"),
        ),
    )

    await storage.delete_private("org-1/missing.pdf")
