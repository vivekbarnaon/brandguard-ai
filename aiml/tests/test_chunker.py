"""Tests for metadata-preserving text chunking."""

import pytest

from app.embeddings.chunker import chunk_document


def test_chunks_small_document_and_preserves_metadata() -> None:
    document = {
        "document_name": "brand_guidelines.pdf",
        "pages": [{"page_number": 2, "text": "Use a clear and professional voice."}],
    }

    chunks = chunk_document(document, "brand-guidelines-001")

    assert len(chunks) == 1
    assert chunks[0]["text"] == "Use a clear and professional voice."
    assert chunks[0]["metadata"] == {
        "document_id": "brand-guidelines-001",
        "document_name": "brand_guidelines.pdf",
        "page_number": 2,
        "chunk_index": 0,
        "section": None,
        "source": "uploaded_pdf",
    }


def test_creates_overlapping_chunks_for_large_text() -> None:
    text = "A" * 1400
    document = {"document_name": "large.pdf", "pages": [{"page_number": 1, "text": text}]}

    chunks = chunk_document(document, "large-document", chunk_size=1000, chunk_overlap=150)

    assert len(chunks) == 2
    assert len(chunks[0]["text"]) == 1000
    assert chunks[0]["text"][-150:] == chunks[1]["text"][:150]


def test_skips_empty_pages() -> None:
    document = {
        "document_name": "brand.pdf",
        "pages": [{"page_number": 1, "text": "   "}, {"page_number": 2, "text": "Approved term"}],
    }

    chunks = chunk_document(document, "brand-document")

    assert len(chunks) == 1
    assert chunks[0]["metadata"]["page_number"] == 2


def test_validates_chunk_settings() -> None:
    document = {"document_name": "brand.pdf", "pages": []}

    with pytest.raises(ValueError, match="smaller than chunk_size"):
        chunk_document(document, "brand-document", chunk_size=10, chunk_overlap=10)
