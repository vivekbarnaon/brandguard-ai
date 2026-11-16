"""Unit tests for Gemini embedding generation using mocked responses."""

from types import SimpleNamespace
from typing import List

import pytest

from app.embeddings.embedder import EmbeddingGenerationError, GeminiEmbedder


def make_response(vectors: List[List[float]]) -> SimpleNamespace:
    return SimpleNamespace(
        embeddings=[SimpleNamespace(values=vector) for vector in vectors]
    )


class MockModels:
    def __init__(self, response: SimpleNamespace = None, error: Exception = None):
        self.response = response
        self.error = error
        self.calls = 0

    def embed_content(self, **kwargs: object) -> SimpleNamespace:
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


class MockClient:
    def __init__(self, models: MockModels):
        self.models = models


def sample_chunks() -> list:
    return [
        {
            "text": "Use a professional tone.",
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


def test_generates_vectors_and_preserves_metadata() -> None:
    models = MockModels(make_response([[0.1, 0.2], [0.3, 0.4]]))
    embedder = GeminiEmbedder(client=MockClient(models), batch_size=2)

    result = embedder.embed_chunks(sample_chunks())

    assert [item["embedding"] for item in result] == [[0.1, 0.2], [0.3, 0.4]]
    assert result[1]["metadata"]["page_number"] == 2
    assert len(result[0]["embedding"]) == 2
    assert models.calls == 1


def test_batches_inputs() -> None:
    models = MockModels(make_response([[0.1, 0.2]]))
    embedder = GeminiEmbedder(client=MockClient(models), batch_size=1)

    result = embedder.embed_chunks(sample_chunks())

    assert len(result) == 2
    assert models.calls == 2


def test_rejects_empty_chunk_text() -> None:
    embedder = GeminiEmbedder(
        client=MockClient(MockModels(make_response([[0.1]])))
    )

    with pytest.raises(ValueError, match="non-empty text"):
        embedder.embed_chunks([{"text": "", "metadata": {}}])


def test_retries_temporary_api_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    models = MockModels(error=RuntimeError("temporary failure"))
    embedder = GeminiEmbedder(
        client=MockClient(models), retry_attempts=3, retry_delay=0
    )
    sleeps = []
    monkeypatch.setattr("app.embeddings.embedder.time.sleep", sleeps.append)

    with pytest.raises(EmbeddingGenerationError, match="3 attempts"):
        embedder.embed_chunks(sample_chunks()[:1])

    assert models.calls == 3
    assert sleeps == [0, 0]
