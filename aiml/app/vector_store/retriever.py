"""Tenant-scoped semantic retrieval from Qdrant."""

from typing import Any, Dict, List, Optional

from qdrant_client.http import models

from app.embeddings.embedder import GeminiEmbedder

from .qdrant_client import QdrantVectorClient


class QdrantRetriever:
    """Embed a query and retrieve only authorized guideline chunks."""

    def __init__(
        self,
        qdrant: QdrantVectorClient,
        embedder: GeminiEmbedder,
    ) -> None:
        self.qdrant = qdrant
        self.embedder = embedder

    def search(
        self,
        query: str,
        organization_id: str,
        limit: int = 5,
        document_id: Optional[str] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Return top matching chunks filtered to one organization."""
        query = query.strip()
        organization_id = organization_id.strip()
        if not query:
            raise ValueError("query must not be empty.")
        if not organization_id:
            raise ValueError("organization_id must not be empty.")
        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        query_vector = self.embedder.embed_query(query)
        conditions = [
            models.FieldCondition(
                key="organization_id",
                match=models.MatchValue(value=organization_id),
            )
        ]
        if document_id:
            conditions.append(
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                )
            )

        query_filter = models.Filter(must=conditions)
        try:
            response = self.qdrant.client.query_points(
                collection_name=self.qdrant.settings.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
            points = response.points
        except Exception as exc:
            raise RuntimeError(f"Qdrant semantic search failed: {exc}") from exc

        return [_format_result(point) for point in points]


def _format_result(point: Any) -> Dict[str, Any]:
    payload = dict(point.payload or {})
    text = payload.pop("text", "")
    return {
        "id": str(point.id),
        "score": point.score,
        "text": text,
        "metadata": payload,
    }
