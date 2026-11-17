"""Internal AI/ML HTTP Microservice for BrandGuard AI."""

from __future__ import annotations

import os
import tempfile
import logging
from typing import Any, List, Optional
import httpx
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.compliance.compliance_engine import ComplianceEngine
from app.compliance.report_generator import generate_report
from app.document_processor.processor import process_pdf
from app.embeddings.chunker import chunk_document
from app.embeddings.embedder import GeminiEmbedder
from app.suggestions.suggestion_engine import SuggestionEngine
from app.vector_store.qdrant_client import QdrantVectorClient
from app.vector_store.retriever import QdrantRetriever
from app.vector_store.vector_store import QdrantVectorStore

app = FastAPI(title="BrandGuard AI - AI/ML Microservice", version="1.0.0")
logger = logging.getLogger(__name__)

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


class GuidelineSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    organisation_id: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "aiml"}


@app.post("/process-document")
async def process_document_endpoint(
    payload: DocumentProcessRequest,
    x_aiml_internal_token: Optional[str] = Header(None, alias="x-aiml-internal-token"),
):
    """Download PDF from signed_url, extract pages, chunk text, and return structured evidence chunks."""
    verify_token(x_aiml_internal_token)
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
            raw_chunks = chunk_document(processed, payload.document_id)
            for chunk in raw_chunks:
                chunk["metadata"]["organization_id"] = payload.organisation_id
            embedded_chunks = GeminiEmbedder().embed_chunks(raw_chunks)
            QdrantVectorStore(QdrantVectorClient()).upsert_chunks(
                embedded_chunks,
                organization_id=payload.organisation_id,
            )

            chunks = []
            for chunk_seq, chunk in enumerate(raw_chunks, start=1):
                metadata = chunk["metadata"]
                chunks.append(
                    {
                        "chunk_id": f"{payload.document_id}-chk-{chunk_seq}",
                        "document_id": payload.document_id,
                        "document_name": payload.storage_path.split("/")[-1],
                        "page_number": metadata.get("page_number", 1),
                        "guideline_text": chunk["text"],
                    }
                )

            return {"status": "processed", "chunks": chunks}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as exc:
        logger.exception("AI/ML document processing failed")
        raise HTTPException(
            status_code=500, detail=f"Failed to process document: {exc}"
        ) from exc


@app.post("/retrieve-guidelines")
async def retrieve_guidelines(
    payload: GuidelineSearchRequest,
    x_aiml_internal_token: Optional[str] = Header(None, alias="x-aiml-internal-token"),
):
    """Retrieve tenant-scoped guideline evidence from Qdrant."""
    verify_token(x_aiml_internal_token)
    try:
        retriever = QdrantRetriever(QdrantVectorClient(), GeminiEmbedder())
        results = retriever.search(
            query=payload.query,
            organization_id=payload.organisation_id,
            limit=payload.limit,
        )
        return {
            "results": [
                {
                    "chunk_id": result["id"],
                    "document_id": result["metadata"].get("document_id"),
                    "document_name": result["metadata"].get("document_name"),
                    "page_number": result["metadata"].get("page_number"),
                    "guideline_text": result["text"],
                }
                for result in results
            ]
        }
    except Exception as exc:
        logger.exception("Qdrant guideline retrieval failed")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve guidelines: {exc}"
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
        logger.exception("AI/ML compliance analysis failed")
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
            original_content=payload.original_content,
            findings=payload.findings,
            guideline_context=context,
            mode=payload.mode,  # type: ignore
        )
        return response.model_dump()
    except Exception as exc:
        logger.exception("AI/ML suggestion generation failed")
        raise HTTPException(
            status_code=500, detail=f"AI/ML suggestion generation failed: {exc}"
        ) from exc
