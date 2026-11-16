"""Chunk processed documents while preserving page and document metadata."""

from typing import Any, Dict, List, Mapping, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter


def _validate_chunk_settings(chunk_size: int, chunk_overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")


def chunk_document(
    document: Mapping[str, Any],
    document_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    source: str = "uploaded_pdf",
) -> List[Dict[str, Any]]:
    """Split a processed PDF document into metadata-preserving chunks."""
    _validate_chunk_settings(chunk_size, chunk_overlap)
    if not document_id.strip():
        raise ValueError("document_id must not be empty.")

    document_name = str(document.get("document_name", "")).strip()
    pages = document.get("pages")
    if not document_name:
        raise ValueError("document must include a document_name.")
    if not isinstance(pages, list):
        raise ValueError("document must include a pages list.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
        strip_whitespace=True,
    )
    chunks: List[Dict[str, Any]] = []
    chunk_index = 0

    for page in pages:
        page_number = page.get("page_number")
        page_text = str(page.get("text", "")).strip()
        if not page_text:
            continue

        page_chunks = splitter.split_text(page_text)
        for text in page_chunks:
            cleaned_text = text.strip()
            if not cleaned_text:
                continue
            chunks.append(
                {
                    "text": cleaned_text,
                    "metadata": {
                        "document_id": document_id,
                        "document_name": document_name,
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                        "section": _find_section(page_text, cleaned_text),
                        "source": source,
                    },
                }
            )
            chunk_index += 1

    return chunks


def _find_section(page_text: str, chunk_text: str) -> Optional[str]:
    """Return no section unless a heading can be identified reliably."""
    del page_text, chunk_text
    return None
