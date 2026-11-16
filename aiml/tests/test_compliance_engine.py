"""Tests for evidence-grounded compliance analysis."""

import json

import pytest

from app.compliance.compliance_engine import (
    ComplianceEngine,
    ComplianceGenerationError,
    ComplianceResponseError,
)


def evidence():
    return [
        {
            "chunk_id": "chunk-voice",
            "document_id": "brand-001",
            "document_name": "brand_guidelines.pdf",
            "page_number": 2,
            "guideline_text": "Use a professional and clear tone.",
        },
        {
            "chunk_id": "chunk-terms",
            "document_id": "brand-001",
            "document_name": "brand_guidelines.pdf",
            "page_number": 3,
            "guideline_text": "Use the product name BrandGuard, not Brand Guarder.",
        },
    ]


def response(findings, status="violations_found"):
    return json.dumps(
        {
            "status": status,
            "summary": "Evidence-based compliance result.",
            "findings": findings,
        }
    )


def finding(
    category="BRAND_VOICE",
    severity="MEDIUM",
    chunk_id="chunk-voice",
    problematic_text="Hey, this is totally awesome!",
):
    return {
        "category": category,
        "severity": severity,
        "problematic_text": problematic_text,
        "explanation": "The wording is inconsistent with the explicit rule.",
        "relevant_brand_rule": "Use a professional and clear tone.",
        "evidence_chunk_id": chunk_id,
        "confidence": 0.91,
    }


def test_fully_compliant_content_returns_no_findings() -> None:
    engine = ComplianceEngine(
        text_generator=lambda prompt: response([], status="compliant")
    )

    result = engine.analyze("BrandGuard provides clear guidance.", evidence())

    assert result["status"] == "compliant"
    assert result["findings"] == []
    assert result["human_review_required"] is True


def test_detects_terminology_violation_with_canonical_source() -> None:
    engine = ComplianceEngine(
        text_generator=lambda prompt: response(
            [
                finding(
                    category="TERMINOLOGY",
                    severity="HIGH",
                    chunk_id="chunk-terms",
                    problematic_text="Brand Guarder",
                )
            ]
        )
    )

    result = engine.analyze("Try Brand Guarder today.", evidence())

    violation = result["findings"][0]
    assert violation["category"] == "TERMINOLOGY"
    assert violation["supporting_document"] == "brand_guidelines.pdf"
    assert violation["page_number"] == 3


def test_detects_tone_violation() -> None:
    engine = ComplianceEngine(
        text_generator=lambda prompt: response([finding()])
    )

    result = engine.analyze("Hey, this is totally awesome!", evidence())

    assert result["findings"][0]["category"] == "BRAND_VOICE"
    assert result["findings"][0]["severity"] == "MEDIUM"


def test_detects_unsupported_claim_separately() -> None:
    claim = finding(
        category="UNSUPPORTED_CLAIM",
        severity="HIGH",
        problematic_text="Our product guarantees 100% success.",
    )
    engine = ComplianceEngine(text_generator=lambda prompt: response([claim]))

    result = engine.analyze("Our product guarantees 100% success.", evidence())

    assert result["findings"][0]["category"] == "UNSUPPORTED_CLAIM"


def test_detects_missing_disclaimer() -> None:
    disclaimer = finding(
        category="DISCLAIMER",
        severity="CRITICAL",
        chunk_id="chunk-voice",
        problematic_text=None,
    )
    engine = ComplianceEngine(
        text_generator=lambda prompt: response([disclaimer])
    )

    result = engine.analyze("Limited-time offer.", evidence())

    assert result["findings"][0]["category"] == "DISCLAIMER"
    assert result["findings"][0]["severity"] == "CRITICAL"


def test_returns_insufficient_evidence_without_calling_gemini() -> None:
    calls = []
    engine = ComplianceEngine(text_generator=calls.append)

    result = engine.analyze("Some marketing copy.", [])

    assert result["status"] == "insufficient_evidence"
    assert result["findings"] == []
    assert calls == []


def test_supports_multiple_simultaneous_violations() -> None:
    findings = [
        finding(),
        finding(
            category="TERMINOLOGY",
            severity="HIGH",
            chunk_id="chunk-terms",
            problematic_text="Brand Guarder",
        ),
    ]
    engine = ComplianceEngine(text_generator=lambda prompt: response(findings))

    result = engine.analyze("Hey, try Brand Guarder!", evidence())

    assert len(result["findings"]) == 2
    assert {item["category"] for item in result["findings"]} == {
        "BRAND_VOICE",
        "TERMINOLOGY",
    }


def test_rejects_finding_without_retrieved_evidence() -> None:
    invalid = finding(chunk_id="not-retrieved")
    engine = ComplianceEngine(text_generator=lambda prompt: response([invalid]))

    with pytest.raises(ComplianceResponseError, match="not retrieved"):
        engine.analyze("Marketing copy.", evidence())


def test_wraps_gemini_failure() -> None:
    engine = ComplianceEngine(
        text_generator=lambda prompt: (_ for _ in ()).throw(
            RuntimeError("Gemini unavailable")
        )
    )

    with pytest.raises(ComplianceGenerationError, match="compliance analysis"):
        engine.analyze("Marketing copy.", evidence())
