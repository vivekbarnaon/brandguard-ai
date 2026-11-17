from typing import Any

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.aiml import (
    ComplianceRequest,
    ComplianceResponse,
    DocumentProcessRequest,
    DocumentProcessResponse,
    SuggestionRequest,
    SuggestionResponse,
)


async def call_aiml(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    headers = {}
    if settings.aiml_internal_token is not None:
        headers["x-aiml-internal-token"] = settings.aiml_internal_token.get_secret_value()
    try:
        async with httpx.AsyncClient(base_url=settings.aiml_service_url, timeout=60) as client:
            response = await client.post(path, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="AI/ML service unavailable or returned invalid data") from exc
    if not isinstance(result, dict):
        raise HTTPException(status_code=502, detail="AI/ML service returned an invalid response")
    return result


async def process_document(request: DocumentProcessRequest) -> DocumentProcessResponse:
    result = await call_aiml(get_settings().aiml_process_path, request.model_dump())
    try:
        return DocumentProcessResponse.model_validate(result)
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail="AI/ML document response failed schema validation") from exc


async def retrieve_guidelines(
    query: str,
    organisation_id: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    result = await call_aiml(
        get_settings().aiml_retrieve_path,
        {
            "query": query,
            "organisation_id": organisation_id,
            "limit": limit,
        },
    )
    evidence = result.get("results")
    if not isinstance(evidence, list):
        raise HTTPException(status_code=502, detail="AI/ML retrieval response was invalid")
    return evidence


async def analyze(request: ComplianceRequest) -> ComplianceResponse:
    result = await call_aiml(get_settings().aiml_analyze_path, request.model_dump())
    try:
        return ComplianceResponse.model_validate(result)
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail="AI/ML compliance response failed schema validation") from exc


async def generate_suggestions(request: SuggestionRequest) -> SuggestionResponse:
    result = await call_aiml(get_settings().aiml_suggestions_path, request.model_dump())
    try:
        return SuggestionResponse.model_validate(result)
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail="AI/ML suggestion response failed schema validation") from exc
