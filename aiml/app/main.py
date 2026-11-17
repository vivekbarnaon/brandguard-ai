"""Internal AI/ML HTTP Microservice for BrandGuard AI."""

from __future__ import annotations

import os
import tempfile
from typing import Any, List, Optional
import httpx
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.compliance.compliance_engine import ComplianceEngine
from app.compliance.report_generator import generate_report
from app.document_processor.processor import process_pdf
from app.embeddings.chunker import chunk_text
from app.suggestions.suggestion_engine import SuggestionEngine

app = FastAPI(title="BrandGuard AI - AI/ML Microservice", version="1.0.0")

INTERNAL_TOKEN = os.getenv("AIML_INTERNAL_TOKEN")


def verify_token(x_aiml_internal_token: Optional[str] = Header(None)) -> None:
    if INTERNAL_TOKEN and x_aiml_internal_token != INTERNAL_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized internal AI/ML request",
        )


class GuidelineEvidenceInput(BaseModel):
    chunk_id: str
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    page_number: Optional[int] = None
    guideline_text: str


class DocumentProcessRequest(BaseModel):
    document_id: str
    organisation_id: str
    storage_path: str
    signed_url: str


class ComplianceRequest(BaseModel):
    content_id: Optional[str] = None
    organisation_id: Optional[str] = None
    original_content: str
    guideline_context: List[GuidelineEvidenceInput]


class SuggestionRequest(BaseModel):
    original_content: str
    findings: List[dict[str, Any]]
    guideline_context: List[GuidelineEvidenceInput]
    mode: str = "minimal_correction"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "aiml"}


@app.post("/process-document")
async def process_document_endpoint(
    payload: DocumentProcessRequest,
    _: None = Header(None, alias="x-aiml-internal-token"),
):
    """Download PDF from signed_url, extract pages, chunk text, and return structured evidence chunks."""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(payload.signed_url)
            resp.raise_for_status()
            pdf_bytes = resp.content

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            processed = process_pdf(tmp_path)
            chunks = []
            chunk_seq = 1
            for page in processed.get("pages", []):
                page_chunks = chunk_text(page.get("text", ""))
                for text_chunk in page_chunks:
                    chunks.append(
                        {
                            "chunk_id": f"{payload.document_id}-chk-{chunk_seq}",
                            "document_id": payload.document_id,
                            "document_name": payload.storage_path.split("/")[-1],
                            "page_number": page.get("page_number", 1),
                            "guideline_text": text_chunk,
                        }
                    )
                    chunk_seq += 1

            return {"status": "processed", "chunks": chunks}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to process document: {exc}"
        ) from exc


@app.post("/analyze")
async def analyze_endpoint(payload: ComplianceRequest):
    """Run evidence-grounded compliance analysis and report generation."""
    try:
        engine = ComplianceEngine()
        context = [c.model_dump() for c in payload.guideline_context]
        result = engine.analyze(
            submitted_content=payload.original_content,
            guideline_context=context,
        )
        report = generate_report(
            document_id=payload.content_id or "content-unknown",
            organisation_id=payload.organisation_id or "org-unknown",
            compliance_result=result,
        )
        return report.model_dump()
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"AI/ML compliance analysis failed: {exc}"
        ) from exc


@app.post("/suggestions")
async def suggestions_endpoint(payload: SuggestionRequest):
    """Run evidence-grounded AI correction suggestions."""
    try:
        engine = SuggestionEngine()
        context = [c.model_dump() for c in payload.guideline_context]
        response = engine.generate(
            submitted_content=payload.original_content,
            findings=payload.findings,
            guideline_context=context,
            mode=payload.mode,  # type: ignore
        )
        return response.model_dump()
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"AI/ML suggestion generation failed: {exc}"
        ) from exc
