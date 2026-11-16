"""Live integration test for the Gemini client."""

import os

import pytest

from app.gemini_client import generate_text


_api_key = os.getenv("GEMINI_API_KEY", "").strip()
_has_api_key = bool(_api_key and _api_key != "your_actual_api_key")


@pytest.mark.skipif(
    not _has_api_key,
    reason="Set GEMINI_API_KEY in aiml/.env to run the live Gemini test.",
)
def test_gemini_generates_brand_governance_explanation() -> None:
    response = generate_text(
        "Explain brand governance in two simple sentences."
    )

    assert response.strip()
