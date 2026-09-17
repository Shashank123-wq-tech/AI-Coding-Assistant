from typing import Any

from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.qdrant_service import QdrantService


class VectorSearchRetriever:
    def __init__(
        self,
        qdrant_service: QdrantService | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        self.qdrant_service = qdrant_service or QdrantService()
        self.embedding_service = embedding_service or EmbeddingService()

    def search(
        self,
        query: str,
        limit: int = 10,
        repository_id: int | None = None,
    ) -> list[dict[str, Any]]:
        query = query.strip()

        if not query:
            return []

        if limit < 1:
            return []

        query_vector = self.embedding_service.embed(query)

        query_filter = None

        if repository_id is not None:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="repository_id",
                        match=MatchValue(value=repository_id),
                    )
                ]
            )

        results = self.qdrant_service.client.query_points(
            collection_name=self.qdrant_service.COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        ).points

        final_results = []

        for result in results:
            payload = result.payload or {}

            final_results.append(
                {
                    "chunk_id": payload.get("chunk_id"),
                    "file_path": payload.get("file_path"),
                    "chunk_type": payload.get("chunk_type"),
                    "language": payload.get("language"),
                    "cell_index": payload.get("cell_index"),
                    "content": payload.get("content"),
                    "metadata": payload.get("metadata", {}),
                    "score": float(result.score),
                }
            )

        return final_results