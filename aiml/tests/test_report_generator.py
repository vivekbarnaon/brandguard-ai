"""Tests for validated compliance report generation."""

import json

import pytest
from pydantic import ValidationError

from app.compliance.report_generator import (
    ComplianceReport,
    EvidenceReference,
    ReportFinding,
    generate_report,
)


def finding(
    severity="MEDIUM",
    chunk_id="chunk-001",
    category="BRAND_VOICE",
):
    return {
        "category": category,
        "severity": severity,
        "problematic_text": "The original sentence",
        "explanation": "The wording does not match the approved tone.",
        "relevant_brand_rule": "Use a professional and approachable tone.",
        "evidence_chunk_id": chunk_id,
        "supporting_document": "brand_guidelines.pdf",
        "document_id": "brand-001",
        "page_number": 2,
        "confidence": 0.91,
        "suggestion": "Use professional wording.",
    }


def test_generates_valid_report() -> None:
    report = generate_report(
        "content-001",
        "org-001",
        {
            "status": "violations_found",
            "summary": "One potential brand inconsistency was found.",
            "findings": [finding()],
        },
    )

    assert isinstance(report, ComplianceReport)
    assert report.overall_status == "NEEDS_REVIEW"
    assert report.compliance_score == 90
    assert report.total_violations == 1
    assert report.findings[0].evidence.page_number == 2
    assert report.findings[0].suggested_correction == "Use professional wording."


def test_rejects_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        ComplianceReport(
            document_id="content-001",
            organisation_id="org-001",
            overall_status="COMPLIANT",
            compliance_score=100,
            total_violations=0,
            findings=[],
        )


def test_rejects_invalid_severity() -> None:
    invalid = finding(severity="URGENT")

    with pytest.raises(ValidationError):
        generate_report(
            "content-001",
            "org-001",
            {"status": "violations_found", "findings": [invalid]},
        )


def test_rejects_invalid_score() -> None:
    with pytest.raises(ValidationError):
        ComplianceReport(
            document_id="content-001",
            organisation_id="org-001",
            overall_status="COMPLIANT",
            compliance_score=101,
            total_violations=0,
            summary="Invalid score",
            findings=[],
        )


def test_empty_findings_can_be_compliant() -> None:
    report = generate_report(
        "content-001",
        "org-001",
        {"status": "compliant", "summary": "No violations.", "findings": []},
    )

    assert report.overall_status == "COMPLIANT"
    assert report.compliance_score == 100
    assert report.total_violations == 0


def test_insufficient_evidence_status() -> None:
    report = generate_report(
        "content-001",
        "org-001",
        {
            "status": "insufficient_evidence",
            "summary": "Guidelines were unavailable.",
            "findings": [],
        },
    )

    assert report.overall_status == "INSUFFICIENT_EVIDENCE"
    assert report.compliance_score == 100


def test_multiple_violations_and_duplicate_penalty() -> None:
    duplicate = finding()
    high = finding(
        severity="HIGH",
        chunk_id="chunk-002",
        category="UNSUPPORTED_CLAIM",
    )

    report = generate_report(
        "content-001",
        "org-001",
        {
            "status": "violations_found",
            "findings": [duplicate, duplicate, high],
        },
    )

    assert report.total_violations == 3
    assert report.compliance_score == 70
    assert report.overall_status == "NON_COMPLIANT"


def test_serializes_to_frontend_json() -> None:
    report = generate_report(
        "content-001",
        "org-001",
        {"status": "compliant", "summary": "All good.", "findings": []},
    )

    payload = json.loads(report.model_dump_json())

    assert payload["document_id"] == "content-001"
    assert payload["organisation_id"] == "org-001"
    assert payload["findings"] == []
