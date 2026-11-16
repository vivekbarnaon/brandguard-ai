"""Batch storage of embedded chunks in Qdrant."""

import uuid
from typing import Any, Dict, List, Mapping, Sequence

from qdrant_client.http.models import PointStruct

from .qdrant_client import QdrantVectorClient


class QdrantVectorStore:
    """Store chunk text, embeddings, and tenant-scoped metadata."""

    def __init__(
        self,
        qdrant: QdrantVectorClient,
        batch_size: int = 100,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")
        self.qdrant = qdrant
        self.batch_size = batch_size

    def upsert_chunks(
        self,
        chunks: Sequence[Mapping[str, Any]],
        organization_id: str,
    ) -> List[str]:
        """Upsert embedded chunks using deterministic, duplicate-safe IDs."""
        organization_id = organization_id.strip()
        if not organization_id:
            raise ValueError("organization_id must not be empty.")
        if not chunks:
            return []

        points = []
        for chunk in chunks:
            text = str(chunk.get("text", "")).strip()
            embedding = list(chunk.get("embedding", []))
            metadata = chunk.get("metadata")
            if not text:
                raise ValueError("Every chunk must contain non-empty text.")
            if not embedding:
                raise ValueError("Every chunk must contain a non-empty embedding.")
            if not isinstance(metadata, Mapping):
                raise ValueError("Every chunk must contain metadata.")

            existing_organization = metadata.get("organization_id")
            if existing_organization and existing_organization != organization_id:
                raise ValueError(
                    "Chunk organization_id does not match the requested organization_id."
                )

            payload = dict(metadata)
            payload["organization_id"] = organization_id
            payload["text"] = text
            point_id = _point_id(organization_id, payload)
            points.append(
                PointStruct(id=point_id, vector=embedding, payload=payload)
            )

        self.qdrant.ensure_collection(len(points[0].vector))
        for start in range(0, len(points), self.batch_size):
            self.qdrant.client.upsert(
                collection_name=self.qdrant.settings.collection_name,
                points=points[start : start + self.batch_size],
                wait=True,
            )
        return [str(point.id) for point in points]


def _point_id(organization_id: str, metadata: Mapping[str, Any]) -> str:
    document_id = str(metadata.get("document_id", "")).strip()
    chunk_index = str(metadata.get("chunk_index", "")).strip()
    if not document_id or not chunk_index:
        raise ValueError("Chunk metadata must include document_id and chunk_index.")
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"brandguard:{organization_id}:{document_id}:{chunk_index}",
        )
    )
