"""Tests for Qdrant configuration and collection management."""

from types import SimpleNamespace

import pytest

from app.vector_store.qdrant_client import (
    QdrantCollectionError,
    QdrantConfigurationError,
    QdrantConnectionError,
    QdrantSettings,
    QdrantVectorClient,
)


class FakeQdrantClient:
    def __init__(self, exists=False, collection=None, error=None):
        self.exists = exists
        self.collection = collection
        self.error = error
        self.created = None

    def get_collections(self):
        if self.error:
            raise self.error
        return SimpleNamespace(collections=[])

    def collection_exists(self, collection_name):
        return self.exists

    def get_collection(self, collection_name):
        return self.collection

    def create_collection(self, **kwargs):
        self.created = kwargs


def settings() -> QdrantSettings:
    return QdrantSettings(
        url="http://localhost:6333",
        api_key=None,
        collection_name="brand_guidelines",
    )


def test_creates_collection_with_requested_dimension() -> None:
    fake = FakeQdrantClient()
    client = QdrantVectorClient(settings=settings(), client=fake)

    client.ensure_collection(3072)

    assert fake.created["collection_name"] == "brand_guidelines"
    assert fake.created["vectors_config"].size == 3072


def test_rejects_existing_collection_with_invalid_dimension() -> None:
    collection = SimpleNamespace(
        config=SimpleNamespace(
            params=SimpleNamespace(vectors=SimpleNamespace(size=768))
        )
    )
    fake = FakeQdrantClient(exists=True, collection=collection)
    client = QdrantVectorClient(settings=settings(), client=fake)

    with pytest.raises(QdrantCollectionError, match="768-dimensional"):
        client.ensure_collection(3072)


def test_verifies_connection_failure() -> None:
    fake = FakeQdrantClient(error=ConnectionError("offline"))
    client = QdrantVectorClient(settings=settings(), client=fake)

    with pytest.raises(QdrantConnectionError, match="Unable to connect"):
        client.verify_connection()


def test_requires_qdrant_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QDRANT_URL", raising=False)

    with pytest.raises(QdrantConfigurationError, match="QDRANT_URL"):
        QdrantSettings.from_env()
