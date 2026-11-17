from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import get_settings


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
