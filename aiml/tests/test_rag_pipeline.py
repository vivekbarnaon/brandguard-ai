"""Unit tests for grounded, tenant-isolated RAG analysis."""

import json

import pytest

from app.rag.rag_pipeline import (
    RAGGenerationError,
    RAGPipeline,
    RAGPipelineError,
    RAGResponseError,
)


class FakeRetriever:
    def __init__(self, results=None, error=None):
        self.results = results or []
        self.error = error
        self.calls = []

    def search(self, query, **kwargs):
        self.calls.append((query, kwargs))
        if self.error:
            raise self.error
        return self.results


def guideline_result(organization_id="org-001"):
    return {
        "id": "chunk-1",
        "score": 0.94,
        "text": "Use a professional and clear tone.",
        "metadata": {
            "organization_id": organization_id,
            "document_id": "brand-001",
            "document_name": "brand_guidelines.pdf",
            "page_number": 2,
            "chunk_index": 0,
            "source": "uploaded_pdf",
        },
    }


def grounded_response():
    return json.dumps(
        {
            "status": "non_compliant",
            "summary": "The submitted content is too casual.",
            "violations": [
                {
                    "rule": "Use a professional and clear tone.",
                    "explanation": "The wording is informal.",
                    "suggestion": "Use professional wording.",
                    "evidence_chunk_id": "chunk-1",
                }
            ],
            "evidence_used": ["chunk-1"],
        }
    )


def test_retrieves_relevant_guidelines_and_tracks_evidence() -> None:
    retriever = FakeRetriever([guideline_result()])
    prompts = []
    pipeline = RAGPipeline(retriever, text_generator=prompts.append)
    prompts.clear()
    pipeline.text_generator = lambda prompt: grounded_response()

    result = pipeline.analyze(
        "org-001",
        "Hey, this product is totally awesome!!!",
        top_k=3,
        score_threshold=0.8,
    )

    assert result["status"] == "non_compliant"
    assert result["evidence"][0]["page_number"] == 2
    assert result["evidence"][0]["guideline_text"] == (
        "Use a professional and clear tone."
    )
    assert retriever.calls[0][1]["organization_id"] == "org-001"
    assert retriever.calls[0][1]["limit"] == 3


def test_no_matching_rules_does_not_call_gemini() -> None:
    calls = []
    pipeline = RAGPipeline(FakeRetriever([]), text_generator=calls.append)

    result = pipeline.analyze("org-001", "Product copy")

    assert result["status"] == "no_relevant_guidelines"
    assert result["analysis"] is None
    assert calls == []


def test_prevents_cross_organization_evidence() -> None:
    pipeline = RAGPipeline(FakeRetriever([guideline_result("other-org")]))

    with pytest.raises(RAGPipelineError, match="organisation isolation"):
        pipeline.analyze("org-001", "Product copy")


def test_passes_organization_id_to_retriever() -> None:
    retriever = FakeRetriever([])
    pipeline = RAGPipeline(retriever)

    pipeline.analyze("org-007", "Product copy", document_id="doc-7")

    assert retriever.calls[0][1]["organization_id"] == "org-007"
    assert retriever.calls[0][1]["document_id"] == "doc-7"


def test_wraps_gemini_failure() -> None:
    pipeline = RAGPipeline(
        FakeRetriever([guideline_result()]),
        text_generator=lambda prompt: (_ for _ in ()).throw(
            RuntimeError("Gemini unavailable")
        ),
    )

    with pytest.raises(RAGGenerationError, match="grounded Gemini"):
        pipeline.analyze("org-001", "Product copy")


def test_rejects_invalid_gemini_response() -> None:
    pipeline = RAGPipeline(
        FakeRetriever([guideline_result()]),
        text_generator=lambda prompt: "not json",
    )

    with pytest.raises(RAGResponseError, match="invalid JSON"):
        pipeline.analyze("org-001", "Product copy")


def test_rejects_empty_submitted_content() -> None:
    pipeline = RAGPipeline(FakeRetriever([]))

    with pytest.raises(ValueError, match="submitted_content"):
        pipeline.analyze("org-001", " ")
