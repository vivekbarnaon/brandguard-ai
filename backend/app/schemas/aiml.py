from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class GuidelineEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1)
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    guideline_text: str = Field(min_length=1)


class EvidenceBatch(BaseModel):
    chunks: list[GuidelineEvidence] = Field(min_length=1)


class DocumentProcessRequest(BaseModel):
    document_id: str = Field(min_length=1)
    organisation_id: str = Field(min_length=1)
    storage_path: str = Field(min_length=1)


class DocumentProcessResponse(BaseModel):
    status: Literal["processed", "failed"]
    chunks_ingested: int = Field(ge=0)


class ComplianceRequest(BaseModel):
    original_content: str = Field(min_length=1)
    guideline_context: list[GuidelineEvidence]


class ComplianceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_status: str = Field(min_length=1)
    compliance_score: int = Field(ge=0, le=100)
    total_violations: int = Field(ge=0)
    summary: str = Field(min_length=1)
    findings: list[dict[str, Any]]
    human_review_required: bool = True
    confidence_note: str = Field(min_length=1)


class SuggestionRequest(BaseModel):
    original_content: str = Field(min_length=1)
    findings: list[dict[str, Any]]
    guideline_context: list[GuidelineEvidence]
    mode: Literal[
        "minimal_correction",
        "professional_rewrite",
        "brand_aligned_rewrite",
    ] = "minimal_correction"


class SuggestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal[
        "suggestions_generated",
        "no_suggestions",
        "insufficient_evidence",
    ]
    original_content: str = Field(min_length=1)
    mode: str
    suggestions: list[dict[str, Any]]
    skipped_finding_ids: list[str] = []
    human_review_required: bool = True
