import pytest
from fastapi import HTTPException

from app.schemas.aiml import (
    ComplianceRequest,
    ComplianceResponse,
    GuidelineEvidence,
    SuggestionRequest,
)
from app.services import aiml


def evidence() -> GuidelineEvidence:
    return GuidelineEvidence(
        chunk_id="chunk-1",
        document_id="document-1",
        document_name="guidelines.pdf",
        page_number=1,
        guideline_text="Use clear, professional language.",
    )


def test_compliance_request_requires_non_empty_evidence_text():
    with pytest.raises(ValueError):
        GuidelineEvidence(chunk_id="chunk-1", guideline_text="")


def test_compliance_response_rejects_invalid_score():
    with pytest.raises(ValueError):
        ComplianceResponse(
            overall_status="compliant",
            compliance_score=101,
            total_violations=0,
            summary="Invalid",
            findings=[],
            confidence_note="Estimated",
        )


def test_suggestion_request_contains_review_context():
    request = SuggestionRequest(
        original_content="Our product is awesome.",
        findings=[{"finding_id": "finding-1"}],
        guideline_context=[evidence()],
    )
    assert request.mode == "minimal_correction"
    assert request.guideline_context[0].chunk_id == "chunk-1"


@pytest.mark.asyncio
async def test_analyze_rejects_invalid_remote_response(monkeypatch):
    async def fake_call(path, payload):
        return {"overall_status": "compliant"}

    monkeypatch.setattr(aiml, "call_aiml", fake_call)
    request = ComplianceRequest(original_content="Copy", guideline_context=[evidence()])

    with pytest.raises(HTTPException) as error:
        await aiml.analyze(request)

    assert error.value.status_code == 502
