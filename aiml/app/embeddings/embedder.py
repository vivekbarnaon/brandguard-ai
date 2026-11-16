"""Gemini embedding generation with batching, validation, and retries."""

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
DEFAULT_BATCH_SIZE = 100
DEFAULT_RETRY_ATTEMPTS = 3


class EmbeddingConfigurationError(RuntimeError):
    """Raised when embedding configuration is incomplete."""


class EmbeddingGenerationError(RuntimeError):
    """Raised when Gemini cannot generate embeddings."""


class GeminiEmbedder:
    """Generate Gemini embeddings for chunk records."""

    def __init__(
        self,
        model: Optional[str] = None,
        client: Optional[Any] = None,
        api_key: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        retry_delay: float = 1.0,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")
        if retry_attempts <= 0:
            raise ValueError("retry_attempts must be greater than zero.")
        if retry_delay < 0:
            raise ValueError("retry_delay cannot be negative.")

        self.model = model or os.getenv(
            "GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        )
        self.batch_size = batch_size
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self._client = client or self._create_client(api_key)

    @staticmethod
    def _create_client(api_key: Optional[str]) -> Any:
        key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        if not key or key == "your_actual_api_key":
            raise EmbeddingConfigurationError(
                "GEMINI_API_KEY is missing. Add it to aiml/.env."
            )
        return genai.Client(api_key=key)

    def embed_chunks(
        self, chunks: Sequence[Mapping[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Return each chunk with its original metadata and embedding vector."""
        if not chunks:
            return []

        texts = []
        for chunk in chunks:
            text = str(chunk.get("text", "")).strip()
            if not text:
                raise ValueError("Every chunk must contain non-empty text.")
            if not isinstance(chunk.get("metadata"), Mapping):
                raise ValueError("Every chunk must contain metadata.")
            texts.append(text)

        embedded_chunks: List[Dict[str, Any]] = []
        for start in range(0, len(chunks), self.batch_size):
            batch_chunks = chunks[start : start + self.batch_size]
            batch_embeddings = self._embed_batch(
                texts[start : start + self.batch_size],
                task_type="RETRIEVAL_DOCUMENT",
            )
            if len(batch_embeddings) != len(batch_chunks):
                raise EmbeddingGenerationError(
                    "Gemini returned a different number of embeddings than inputs."
                )

            for chunk, embedding in zip(batch_chunks, batch_embeddings):
                embedded_chunks.append(
                    {
                        "text": str(chunk["text"]).strip(),
                        "metadata": dict(chunk["metadata"]),
                        "embedding": embedding,
                    }
                )
        return embedded_chunks

    def embed_query(self, query: str) -> List[float]:
        """Generate one retrieval-query embedding."""
        query = query.strip()
        if not query:
            raise ValueError("query must not be empty.")
        embeddings = self._embed_batch([query], task_type="RETRIEVAL_QUERY")
        return embeddings[0]

    def _embed_batch(
        self, texts: Sequence[str], task_type: str
    ) -> List[List[float]]:
        last_error: Optional[Exception] = None
        for attempt in range(self.retry_attempts):
            try:
                response = self._client.models.embed_content(
                    model=self.model,
                    contents=list(texts),
                    config=types.EmbedContentConfig(task_type=task_type),
                )
                embeddings = getattr(response, "embeddings", None) or []
                vectors = [list(embedding.values or []) for embedding in embeddings]
                if not vectors or any(not vector for vector in vectors):
                    raise EmbeddingGenerationError(
                        "Gemini returned an empty embedding response."
                    )
                dimensions = {len(vector) for vector in vectors}
                if len(dimensions) != 1:
                    raise EmbeddingGenerationError(
                        "Gemini returned embeddings with inconsistent dimensions."
                    )
                return vectors
            except EmbeddingGenerationError:
                raise
            except Exception as exc:
                last_error = exc
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2**attempt))

        raise EmbeddingGenerationError(
            f"Gemini embedding generation failed after "
            f"{self.retry_attempts} attempts: {last_error}"
        ) from last_error
