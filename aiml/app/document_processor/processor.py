"""High-level PDF document processing service."""

from pathlib import Path
from typing import Any, Dict

from .pdf_extractor import PathInput, extract_pages
from .text_cleaner import clean_text


def process_pdf(pdf_path: PathInput) -> Dict[str, Any]:
    """Extract and clean a PDF, returning page-level structured data."""
    path = Path(pdf_path)
    extracted_pages = extract_pages(path)
    pages = [
        {
            "page_number": page.page_number,
            "text": clean_text(page.text),
        }
        for page in extracted_pages
    ]

    return {
        "document_name": path.name,
        "total_pages": len(pages),
        "pages": pages,
        "status": "processed",
    }
