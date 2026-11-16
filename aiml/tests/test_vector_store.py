"""Tests for batch upsert and duplicate-safe Qdrant point IDs."""

from types import SimpleNamespace

from app.vector_store.qdrant_client import QdrantSettings
from app.vector_store.vector_store import QdrantVectorStore


class FakeQdrantClient:
    def __init__(self):
        self.upserts = []

    def upsert(self, **kwargs):
        self.upserts.append(kwargs)


class FakeQdrant:
    def __init__(self):
        self.settings = QdrantSettings(
            url="http://localhost:6333",
            api_key=None,
            collection_name="brand_guidelines",
        )
        self.client = FakeQdrantClient()
        self.dimensions = None

    def ensure_collection(self, vector_size):
        self.dimensions = vector_size


def chunks():
    return [
        {
            "text": "Use a professional tone.",
            "embedding": [0.1, 0.2],
            "metadata": {
                "document_id": "brand-001",
                "document_name": "brand.pdf",
                "page_number": 1,
                "chunk_index": 0,
                "section": None,
                "source": "uploaded_pdf",
            },
        },
        {
            "text": "Avoid unsupported claims.",
            "embedding": [0.3, 0.4],
            "metadata": {
                "document_id": "brand-001",
                "document_name": "brand.pdf",
                "page_number": 2,
                "chunk_index": 1,
                "section": "Claims",
                "source": "uploaded_pdf",
            },
        },
    ]


def test_upserts_vectors_and_tenant_metadata() -> None:
    qdrant = FakeQdrant()
    store = QdrantVectorStore(qdrant, batch_size=1)

    point_ids = store.upsert_chunks(chunks(), "org-001")

    assert len(point_ids) == 2
    assert qdrant.dimensions == 2
    assert len(qdrant.client.upserts) == 2
    payload = qdrant.client.upserts[0]["points"][0].payload
    assert payload["organization_id"] == "org-001"
    assert payload["text"] == "Use a professional tone."


def test_same_chunk_gets_same_point_id() -> None:
    first_qdrant = FakeQdrant()
    second_qdrant = FakeQdrant()

    first_ids = QdrantVectorStore(first_qdrant).upsert_chunks(chunks()[:1], "org-001")
    second_ids = QdrantVectorStore(second_qdrant).upsert_chunks(chunks()[:1], "org-001")

    assert first_ids == second_ids


def test_rejects_mismatched_tenant_metadata() -> None:
    qdrant = FakeQdrant()
    store = QdrantVectorStore(qdrant)
    mismatched = chunks()[:1]
    mismatched[0]["metadata"]["organization_id"] = "other-org"

    try:
        store.upsert_chunks(mismatched, "org-001")
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("Expected mismatched tenant metadata to fail.")
