"""Validated, frontend-ready compliance reports."""

import re
from typing import Any, Dict, List, Literal, Mapping, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationError


ViolationCategory = Literal[
    "BRAND_VOICE",
    "TERMINOLOGY",
    "PROHIBITED_LANGUAGE",
    "UNSUPPORTED_CLAIM",
    "PRODUCT_ACCURACY",
    "DISCLAIMER",
    "MESSAGING",
    "OTHER",
]
Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
OverallStatus = Literal[
    "COMPLIANT",
    "NEEDS_REVIEW",
    "NON_COMPLIANT",
    "INSUFFICIENT_EVIDENCE",
]

DEFAULT_SEVERITY_PENALTIES: Dict[str, int] = {
    "CRITICAL": 30,
    "HIGH": 20,
    "MEDIUM": 10,
    "LOW": 5,
    "INFO": 0,
}
NON_COMPLIANT_SEVERITIES = {"CRITICAL", "HIGH"}


class EvidenceReference(BaseModel):
    """Canonical source reference for one compliance finding."""

    model_config = ConfigDict(extra="forbid")

    document_id: Optional[str] = None
    document_name: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    chunk_id: Optional[str] = None


class ReportFinding(BaseModel):
    """Validated violation or evidence-backed recommendation."""

    model_config = ConfigDict(extra="forbid")

    category: ViolationCategory
    severity: Severity
    problematic_text: Optional[str] = None
    explanation: str = Field(min_length=1)
    rule: Optional[str] = None
    evidence: Optional[EvidenceReference] = None
    confidence: float = Field(ge=0, le=1)
    suggested_correction: Optional[str] = None


class ComplianceReport(BaseModel):
    """Stable JSON contract for frontend compliance results."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)
    organisation_id: str = Field(min_length=1)
    overall_status: OverallStatus
    compliance_score: int = Field(ge=0, le=100)
    total_violations: int = Field(ge=0)
    summary: str = Field(min_length=1)
    findings: List[ReportFinding]
    human_review_required: bool = True
    confidence_note: str = (
        "Confidence is an estimated model confidence, not a statistically "
        "calibrated probability."
    )


def generate_report(
    document_id: str,
    organisation_id: str,
    compliance_result: Mapping[str, Any],
    severity_penalties: Optional[Mapping[str, int]] = None,
) -> ComplianceReport:
    """Convert compliance-engine output into a validated report."""
    findings_input = compliance_result.get("findings", [])
    if not isinstance(findings_input, Sequence) or isinstance(
        findings_input, (str, bytes)
    ):
        raise ValueError("compliance_result findings must be a sequence.")

    penalties = _validate_penalties(severity_penalties)
    findings = [_to_report_finding(item) for item in findings_input]
    score = calculate_score(findings, penalties)
    status = _determine_status(compliance_result, findings)
    summary = str(compliance_result.get("summary", "")).strip()
    if not summary:
        summary = _default_summary(status, len(findings))

    return ComplianceReport(
        document_id=document_id,
        organisation_id=organisation_id,
        overall_status=status,
        compliance_score=score,
        total_violations=len(findings),
        summary=summary,
        findings=findings,
        human_review_required=True,
    )


def calculate_score(
    findings: Sequence[ReportFinding],
    severity_penalties: Optional[Mapping[str, int]] = None,
) -> int:
    """Calculate 100 minus unique issue penalties, clamped to 0..100."""
    penalties = _validate_penalties(severity_penalties)
    seen_issues = set()
    total_penalty = 0
    for finding in findings:
        issue_key = _issue_key(finding)
        if issue_key in seen_issues:
            continue
        seen_issues.add(issue_key)
        total_penalty += penalties[finding.severity]
    return max(0, min(100, 100 - total_penalty))


def _to_report_finding(item: Any) -> ReportFinding:
    if not isinstance(item, Mapping):
        raise ValueError("Every compliance finding must be an object.")

    evidence = item.get("evidence")
    if evidence is None and any(
        item.get(key) is not None
        for key in ("evidence_chunk_id", "supporting_document", "document_id", "page_number")
    ):
        evidence = {
            "chunk_id": item.get("evidence_chunk_id"),
            "document_id": item.get("document_id"),
            "document_name": item.get("supporting_document"),
            "page_number": item.get("page_number"),
        }

    try:
        return ReportFinding(
            category=item.get("category"),
            severity=item.get("severity"),
            problematic_text=item.get("problematic_text"),
            explanation=item.get("explanation", ""),
            rule=item.get("rule", item.get("relevant_brand_rule")),
            evidence=evidence,
            confidence=item.get("confidence"),
            suggested_correction=item.get(
                "suggested_correction", item.get("suggestion")
            ),
        )
    except ValidationError:
        raise


def _determine_status(
    compliance_result: Mapping[str, Any],
    findings: Sequence[ReportFinding],
) -> str:
    source_status = str(compliance_result.get("status", "")).lower()
    if source_status == "insufficient_evidence" or any(
        finding.evidence is None for finding in findings
    ):
        return "INSUFFICIENT_EVIDENCE"
    if not findings and source_status == "compliant":
        return "COMPLIANT"
    if any(finding.severity in NON_COMPLIANT_SEVERITIES for finding in findings):
        return "NON_COMPLIANT"
    return "NEEDS_REVIEW"


def _issue_key(finding: ReportFinding) -> str:
    evidence_id = finding.evidence.chunk_id if finding.evidence else "no-evidence"
    problematic = re.sub(r"\s+", " ", finding.problematic_text or "").strip().lower()
    return f"{finding.category}|{evidence_id}|{problematic}"


def _validate_penalties(
    severity_penalties: Optional[Mapping[str, int]],
) -> Dict[str, int]:
    penalties = dict(DEFAULT_SEVERITY_PENALTIES)
    if severity_penalties:
        for severity, penalty in severity_penalties.items():
            if severity not in penalties:
                raise ValueError(f"Unknown severity penalty: {severity}")
            if not isinstance(penalty, int) or penalty < 0:
                raise ValueError("Severity penalties must be non-negative integers.")
            penalties[severity] = penalty
    return penalties


def _default_summary(status: str, finding_count: int) -> str:
    if status == "COMPLIANT":
        return "No evidence-backed brand violations were found."
    if status == "INSUFFICIENT_EVIDENCE":
        return "There was not enough guideline evidence to complete the assessment."
    return f"{finding_count} potential brand inconsistency(ies) require review."
