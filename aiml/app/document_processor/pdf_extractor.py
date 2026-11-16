"""PDF validation and page-by-page text extraction."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

import fitz


PathInput = Union[str, Path]


class PDFProcessingError(RuntimeError):
    """Base error for PDF validation and extraction failures."""


class PDFValidationError(PDFProcessingError):
    """Raised when the input path is missing or is not a PDF file."""


class InvalidPDFError(PDFProcessingError):
    """Raised when the input cannot be opened as a valid PDF."""


class EmptyDocumentError(PDFProcessingError):
    """Raised when a PDF has no extractable text."""


@dataclass(frozen=True)
class ExtractedPage:
    """Text extracted from one PDF page."""

    page_number: int
    text: str


def validate_pdf_path(pdf_path: PathInput) -> Path:
    """Validate and return a PDF path."""
    path = Path(pdf_path)
    if not path.exists():
        raise PDFValidationError(f"PDF file does not exist: {path}")
    if not path.is_file():
        raise PDFValidationError(f"PDF path is not a file: {path}")
    if path.suffix.lower() != ".pdf":
        raise PDFValidationError(f"Expected a .pdf file, received: {path.name}")
    if path.stat().st_size == 0:
        raise PDFValidationError(f"PDF file is empty: {path}")
    return path


def extract_pages(pdf_path: PathInput) -> List[ExtractedPage]:
    """Extract raw text from each page while preserving page numbers."""
    path = validate_pdf_path(pdf_path)

    try:
        document = fitz.open(path)
    except (fitz.FileDataError, OSError) as exc:
        raise InvalidPDFError(f"Could not open PDF '{path.name}': {exc}") from exc

    try:
        if document.page_count == 0:
            raise EmptyDocumentError(f"PDF contains no pages: {path.name}")

        pages = [
            ExtractedPage(
                page_number=page_number,
                text=document.load_page(page_number - 1).get_text("text"),
            )
            for page_number in range(1, document.page_count + 1)
        ]
    finally:
        document.close()

    if not any(page.text.strip() for page in pages):
        raise EmptyDocumentError(
            f"PDF '{path.name}' contains no extractable text. "
            "Scanned PDFs require OCR support."
        )
    return pages
