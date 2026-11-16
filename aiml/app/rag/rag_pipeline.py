"""Reusable, tenant-isolated RAG pipeline for brand guideline analysis."""

import json
import re
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

from app.gemini_client import generate_text
from app.vector_store.retriever import QdrantRetriever

from .prompts import build_rag_prompt


class RAGPipelineError(RuntimeError):
    """Base error for RAG processing failures."""


class RAGGenerationError(RAGPipelineError):
    """Raised when Gemini cannot generate a grounded response."""


class RAGResponseError(RAGPipelineError):
    """Raised when Gemini returns an invalid structured response."""


TextGenerator = Callable[[str], str]


class RAGPipeline:
    """Retrieve tenant-scoped evidence and ask Gemini for grounded analysis."""

    def __init__(
        self,
        retriever: QdrantRetriever,
        text_generator: TextGenerator = generate_text,
    ) -> None:
        self.retriever = retriever
        self.text_generator = text_generator

    def analyze(
        self,
        organization_id: str,
        submitted_content: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return a grounded analysis with the retrieved evidence attached."""
        organization_id = organization_id.strip()
        submitted_content = submitted_content.strip()
        if not organization_id:
            raise ValueError("organization_id must not be empty.")
        if not submitted_content:
            raise ValueError("submitted_content must not be empty.")

        try:
            retrieved = self.retriever.search(
                submitted_content,
                organization_id=organization_id,
                limit=top_k,
                document_id=document_id,
                score_threshold=score_threshold,
            )
        except Exception as exc:
            raise RAGPipelineError(
                f"Unable to retrieve brand guidelines: {exc}"
            ) from exc

        evidence = _build_evidence(retrieved, organization_id)
        if not evidence:
            return {
                "status": "no_relevant_guidelines",
                "organization_id": organization_id,
                "submitted_content": submitted_content,
                "analysis": None,
                "evidence": [],
            }

        prompt = build_rag_prompt(submitted_content, evidence)
        try:
            raw_response = self.text_generator(prompt)
        except Exception as exc:
            raise RAGGenerationError(
                f"Unable to generate grounded Gemini response: {exc}"
            ) from exc

        analysis = _parse_response(raw_response)
        return {
            "status": analysis["status"],
            "organization_id": organization_id,
            "submitted_content": submitted_content,
            "analysis": analysis,
            "evidence": evidence,
        }


def _build_evidence(
    retrieved: Sequence[Mapping[str, Any]],
    organization_id: str,
) -> List[Dict[str, Any]]:
    evidence = []
    for result in retrieved:
        metadata = result.get("metadata")
        if not isinstance(metadata, Mapping):
            continue
        if metadata.get("organization_id") != organization_id:
            raise RAGPipelineError("Retrieved evidence failed organisation isolation.")

        evidence.append(
            {
                "chunk_id": str(result.get("id", "")),
                "document_id": metadata.get("document_id"),
                "document_name": metadata.get("document_name"),
                "page_number": metadata.get("page_number"),
                "guideline_text": str(result.get("text", "")),
                "score": result.get("score"),
            }
        )
    return [item for item in evidence if item["chunk_id"] and item["guideline_text"]]


def _parse_response(raw_response: str) -> Dict[str, Any]:
    if not isinstance(raw_response, str) or not raw_response.strip():
        raise RAGResponseError("Gemini returned an empty RAG response.")

    response_text = raw_response.strip()
    fenced_match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
    if fenced_match:
        response_text = fenced_match.group(1).strip()

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise RAGResponseError("Gemini returned invalid JSON for the RAG response.") from exc

    if not isinstance(parsed, dict):
        raise RAGResponseError("Gemini RAG response must be a JSON object.")
    if parsed.get("status") not in {
        "compliant",
        "non_compliant",
        "insufficient_evidence",
    }:
        raise RAGResponseError("Gemini RAG response has an invalid status.")
    if not isinstance(parsed.get("summary"), str):
        raise RAGResponseError("Gemini RAG response must include a summary.")
    if not isinstance(parsed.get("violations"), list):
        raise RAGResponseError("Gemini RAG response must include violations.")
    if not isinstance(parsed.get("evidence_used"), list):
        raise RAGResponseError("Gemini RAG response must include evidence_used.")
    return parsed
