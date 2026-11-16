"""Tests for PDF extraction and document processing."""

from pathlib import Path

import fitz
import pytest

from app.document_processor.pdf_extractor import (
    EmptyDocumentError,
    InvalidPDFError,
    PDFValidationError,
    extract_pages,
)
from app.document_processor.processor import process_pdf


def create_pdf(path: Path, pages: list[str]) -> Path:
    document = fitz.open()
    for page_text in pages:
        page = document.new_page()
        page.insert_text((72, 72), page_text)
    document.save(path)
    document.close()
    return path


def test_extracts_text_from_valid_pdf(tmp_path: Path) -> None:
    pdf_path = create_pdf(tmp_path / "brand_guidelines.pdf", ["Use a professional tone."])

    pages = extract_pages(pdf_path)

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "Use a professional tone." in pages[0].text


def test_processes_multiple_pages_and_preserves_page_numbers(tmp_path: Path) -> None:
    pdf_path = create_pdf(
        tmp_path / "multi_page.pdf",
        ["Brand voice: clear and helpful.", "Avoid unsupported claims."],
    )

    result = process_pdf(pdf_path)

    assert result["document_name"] == "multi_page.pdf"
    assert result["total_pages"] == 2
    assert result["status"] == "processed"
    assert [page["page_number"] for page in result["pages"]] == [1, 2]
    assert result["pages"][1]["text"] == "Avoid unsupported claims."


def test_detects_empty_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "empty.pdf"
    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(EmptyDocumentError, match="no extractable text"):
        extract_pages(pdf_path)


def test_rejects_invalid_pdf(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.pdf"
    invalid_path.write_text("This is not a PDF.", encoding="utf-8")

    with pytest.raises(InvalidPDFError):
        extract_pages(invalid_path)


def test_rejects_missing_pdf() -> None:
    with pytest.raises(PDFValidationError, match="does not exist"):
        extract_pages("/tmp/brandguard-missing-file.pdf")


def test_rejects_non_pdf_file(tmp_path: Path) -> None:
    text_path = tmp_path / "guidelines.txt"
    text_path.write_text("Brand voice", encoding="utf-8")

    with pytest.raises(PDFValidationError, match="Expected a .pdf"):
        extract_pages(text_path)
