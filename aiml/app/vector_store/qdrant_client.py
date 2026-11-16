"""Qdrant client configuration, connectivity, and collection management."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class QdrantConfigurationError(RuntimeError):
    """Raised when Qdrant configuration is incomplete or invalid."""


class QdrantConnectionError(RuntimeError):
    """Raised when Qdrant cannot be reached."""


class QdrantCollectionError(RuntimeError):
    """Raised when a Qdrant collection cannot be created or validated."""


@dataclass(frozen=True)
class QdrantSettings:
    """Connection and collection settings for Qdrant."""

    url: str
    api_key: Optional[str]
    collection_name: str

    @classmethod
    def from_env(cls) -> "QdrantSettings":
        url = os.getenv("QDRANT_URL", "").strip()
        if not url:
            raise QdrantConfigurationError(
                "QDRANT_URL is missing. Add it to aiml/.env."
            )

        collection_name = os.getenv("QDRANT_COLLECTION", "brand_guidelines").strip()
        if not collection_name:
            raise QdrantConfigurationError(
                "QDRANT_COLLECTION must not be empty."
            )

        api_key = os.getenv("QDRANT_API_KEY", "").strip() or None
        return cls(url=url, api_key=api_key, collection_name=collection_name)


class QdrantVectorClient:
    """Manage a Qdrant client and one configured collection."""

    def __init__(
        self,
        settings: Optional[QdrantSettings] = None,
        client: Optional[Any] = None,
    ) -> None:
        self.settings = settings or QdrantSettings.from_env()
        self.client = client or QdrantClient(
            url=self.settings.url,
            api_key=self.settings.api_key,
        )

    def verify_connection(self) -> None:
        """Raise an explicit error if Qdrant is unavailable."""
        try:
            self.client.get_collections()
        except Exception as exc:
            raise QdrantConnectionError(
                f"Unable to connect to Qdrant at {self.settings.url}: {exc}"
            ) from exc

    def collection_exists(self) -> bool:
        """Return whether the configured collection exists."""
        try:
            return bool(self.client.collection_exists(self.settings.collection_name))
        except AttributeError:
            try:
                collections = self.client.get_collections().collections
                return any(
                    collection.name == self.settings.collection_name
                    for collection in collections
                )
            except Exception as exc:
                raise QdrantCollectionError(
                    f"Unable to check collection '{self.settings.collection_name}': {exc}"
                ) from exc
        except Exception as exc:
            raise QdrantCollectionError(
                f"Unable to check collection '{self.settings.collection_name}': {exc}"
            ) from exc

    def ensure_collection(self, vector_size: int) -> None:
        """Create the collection or validate its existing vector dimension."""
        if vector_size <= 0:
            raise ValueError("vector_size must be greater than zero.")

        try:
            if self.collection_exists():
                collection = self.client.get_collection(self.settings.collection_name)
                existing_size = _get_vector_size(collection)
                if existing_size != vector_size:
                    raise QdrantCollectionError(
                        f"Collection '{self.settings.collection_name}' uses "
                        f"{existing_size}-dimensional vectors, not {vector_size}."
                    )
                return

            self.client.create_collection(
                collection_name=self.settings.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE,
                ),
            )
        except QdrantCollectionError:
            raise
        except Exception as exc:
            raise QdrantCollectionError(
                f"Unable to create collection '{self.settings.collection_name}': {exc}"
            ) from exc


def _get_vector_size(collection: Any) -> int:
    config = getattr(collection, "config", None)
    params = getattr(config, "params", None)
    vectors = getattr(params, "vectors", None)
    size = getattr(vectors, "size", None)
    if size is None and isinstance(vectors, dict):
        size = vectors.get("size")
    if size is None:
        raise QdrantCollectionError(
            "Unable to determine the existing collection vector dimension."
        )
    return int(size)
