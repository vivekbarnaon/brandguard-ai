"""Tests for evidence-grounded correction suggestions."""

import json

import pytest

from app.suggestions.suggestion_engine import (
    SuggestionEngine,
    SuggestionGenerationError,
    SuggestionResponseError,
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
            "guideline_text": "Use BrandGuard, not Brand Guarder.",
        },
    ]


def finding(chunk_id="chunk-voice", category="BRAND_VOICE", finding_id=None):
    item = {
        "category": category,
        "severity": "MEDIUM",
        "problematic_text": "Hey, this is totally awesome!",
        "explanation": "The wording is too casual.",
        "evidence_chunk_id": chunk_id,
    }
    if finding_id:
        item["finding_id"] = finding_id
    return item


def suggestion_response(items):
    return json.dumps({"suggestions": items})


def suggestion_item(
    finding_id="finding-001",
    chunk_id="chunk-voice",
    original_text="Hey, this is totally awesome!",
    suggested_text="Our product delivers a clear and valuable experience.",
):
    return {
        "finding_id": finding_id,
        "original_text": original_text,
        "suggested_text": suggested_text,
        "reason": "The revision follows the approved professional tone.",
        "supporting_rule": "Use a professional and clear tone.",
        "evidence": {
            "document_id": "brand-001",
            "document_name": "brand_guidelines.pdf",
            "page_number": 2,
            "chunk_id": chunk_id,
        },
        "requires_human_review": True,
    }


def test_generates_brand_voice_correction() -> None:
    engine = SuggestionEngine(
        lambda prompt: suggestion_response([suggestion_item()])
    )

    result = engine.generate(
        "Hey, this is totally awesome!",
        [finding()],
        evidence(),
        mode="minimal_correction",
    )

    assert result.status == "suggestions_generated"
    assert result.suggestions[0].suggested_text.startswith("Our product")
    assert result.suggestions[0].requires_human_review is True


def test_generates_terminology_correction() -> None:
    item = suggestion_item(
        chunk_id="chunk-terms",
        original_text="Try Brand Guarder.",
        suggested_text="Try BrandGuard.",
    )
    engine = SuggestionEngine(lambda prompt: suggestion_response([item]))

    result = engine.generate(
        "Try Brand Guarder.",
        [finding("chunk-terms", "TERMINOLOGY")],
        evidence(),
        mode="brand_aligned_rewrite",
    )

    assert result.suggestions[0].suggested_text == "Try BrandGuard."
    assert result.suggestions[0].evidence.page_number == 3


def test_supports_unsupported_claim_correction() -> None:
    item = suggestion_item(
        original_text="Our product guarantees 100% success.",
        suggested_text="Our product is designed to support your workflow.",
    )
    claim = finding(category="UNSUPPORTED_CLAIM")
    engine = SuggestionEngine(lambda prompt: suggestion_response([item]))

    result = engine.generate(
        "Our product guarantees 100% success.",
        [claim],
        evidence(),
        mode="professional_rewrite",
    )

    assert "guarantees 100%" not in result.suggestions[0].suggested_text


def test_supports_missing_disclaimer_suggestion() -> None:
    item = suggestion_item(
        original_text="Limited-time offer.",
        suggested_text="Limited-time offer. Terms and conditions apply.",
    )
    disclaimer = finding(category="DISCLAIMER")
    engine = SuggestionEngine(lambda prompt: suggestion_response([item]))

    result = engine.generate(
        "Limited-time offer.",
        [disclaimer],
        evidence(),
    )

    assert "Terms and conditions apply." in result.suggestions[0].suggested_text


def test_marks_missing_evidence_without_calling_gemini() -> None:
    calls = []
    engine = SuggestionEngine(calls.append)

    result = engine.generate(
        "Marketing copy.",
        [finding("missing-chunk")],
        evidence(),
    )

    assert result.status == "insufficient_evidence"
    assert result.suggestions == []
    assert result.skipped_finding_ids == ["finding-001"]
    assert calls == []


def test_generates_multiple_suggestions() -> None:
    items = [
        suggestion_item(),
        suggestion_item(
            finding_id="finding-002",
            chunk_id="chunk-terms",
            original_text="Try Brand Guarder.",
            suggested_text="Try BrandGuard.",
        ),
    ]
    engine = SuggestionEngine(lambda prompt: suggestion_response(items))

    result = engine.generate(
        "Hey, try Brand Guarder.",
        [finding(), finding("chunk-terms", "TERMINOLOGY", "finding-002")],
        evidence(),
    )

    assert len(result.suggestions) == 2


def test_wraps_gemini_error() -> None:
    engine = SuggestionEngine(
        lambda prompt: (_ for _ in ()).throw(RuntimeError("Gemini unavailable"))
    )

    with pytest.raises(SuggestionGenerationError, match="suggestions"):
        engine.generate("Marketing copy.", [finding()], evidence())


def test_rejects_invalid_generated_response() -> None:
    engine = SuggestionEngine(lambda prompt: "not json")

    with pytest.raises(SuggestionResponseError, match="invalid JSON"):
        engine.generate("Marketing copy.", [finding()], evidence())
