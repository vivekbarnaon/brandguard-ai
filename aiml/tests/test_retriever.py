"""Tests for tenant-scoped semantic retrieval."""

from types import SimpleNamespace

import pytest

from app.vector_store.retriever import QdrantRetriever
from app.vector_store.qdrant_client import QdrantSettings


class FakeEmbedder:
    def embed_query(self, query):
        self.query = query
        return [0.1, 0.2]


class FakeQdrantClient:
    def __init__(self, points=None, error=None):
        self.points = points or []
        self.error = error
        self.query_kwargs = None

    def query_points(self, **kwargs):
        if self.error:
            raise self.error
        self.query_kwargs = kwargs
        return SimpleNamespace(points=self.points)


class FakeQdrant:
    def __init__(self, client):
        self.client = client
        self.settings = QdrantSettings(
            url="http://localhost:6333",
            api_key=None,
            collection_name="brand_guidelines",
        )


def test_retrieves_results_with_organization_and_document_filters() -> None:
    point = SimpleNamespace(
        id="point-1",
        score=0.91,
        payload={
            "text": "Use a professional voice.",
            "organization_id": "org-001",
            "document_id": "brand-001",
            "page_number": 1,
        },
    )
    client = FakeQdrantClient([point])
    retriever = QdrantRetriever(FakeQdrant(client), FakeEmbedder())

    results = retriever.search(
        "What tone should we use?",
        organization_id="org-001",
        document_id="brand-001",
        limit=3,
    )

    assert results == [
        {
            "id": "point-1",
            "score": 0.91,
            "text": "Use a professional voice.",
            "metadata": {
                "organization_id": "org-001",
                "document_id": "brand-001",
                "page_number": 1,
            },
        }
    ]
    conditions = client.query_kwargs["query_filter"].must
    assert {condition.key for condition in conditions} == {
        "organization_id",
        "document_id",
    }


def test_rejects_missing_tenant() -> None:
    retriever = QdrantRetriever(
        FakeQdrant(FakeQdrantClient()), FakeEmbedder()
    )

    with pytest.raises(ValueError, match="organization_id"):
        retriever.search("brand tone", organization_id="")


def test_surfaces_qdrant_search_failure() -> None:
    client = FakeQdrantClient(error=ConnectionError("offline"))
    retriever = QdrantRetriever(FakeQdrant(client), FakeEmbedder())

    with pytest.raises(RuntimeError, match="semantic search failed"):
        retriever.search("brand tone", organization_id="org-001")
