"""Reusable client helpers for the Google Gemini API."""

import os
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types


_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_FILE)
logger = logging.getLogger(__name__)


class GeminiConfigurationError(RuntimeError):
    """Raised when the Gemini client is not configured correctly."""


class GeminiGenerationError(RuntimeError):
    """Raised when Gemini cannot generate a response."""


def _get_configuration() -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "").strip()

    if not api_key or api_key == "your_actual_api_key":
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is missing. Add your Google Gemini API key to aiml/.env."
        )
    if not model:
        raise GeminiConfigurationError(
            "GEMINI_MODEL is missing. Add a supported model ID to aiml/.env."
        )

    return api_key, model


def generate_text(prompt: str, model: Optional[str] = None) -> str:
    """Generate text from Gemini using the configured API key and model."""
    if not prompt.strip():
        raise ValueError("The Gemini prompt must not be empty.")

    api_key, configured_model = _get_configuration()
    selected_model = model or configured_model

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
    except Exception as exc:
        logger.exception("Gemini generation failed for model %s", selected_model)
        raise GeminiGenerationError(
            f"Gemini generation failed for model '{selected_model}': {exc}"
        ) from exc

    text = response.text
    if not text:
        raise GeminiGenerationError("Gemini returned an empty response.")
    return text.strip()
