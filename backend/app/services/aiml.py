from typing import Any

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.aiml import (
    ComplianceRequest,
    ComplianceResponse,
    SuggestionRequest,
    SuggestionResponse,
)


async def call_aiml(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(base_url=settings.aiml_service_url, timeout=60) as client:
            response = await client.post(path, json=payload)
            response.raise_for_status()
            result = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="AI/ML service unavailable or returned invalid data") from exc
    if not isinstance(result, dict):
        raise HTTPException(status_code=502, detail="AI/ML service returned an invalid response")
    return result


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
