from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


class QdrantService:
    COLLECTION_NAME = "code_chunks"
    VECTOR_SIZE = 384

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.client = QdrantClient(
            host=host,
            port=port,
        )

    def collection_exists(self) -> bool:
        collections = self.client.get_collections().collections

        return any(
            collection.name == self.COLLECTION_NAME
            for collection in collections
        )

    def create_collection(self) -> None:
        if self.collection_exists():
            return

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=self.VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def get_collection_info(self) -> Any:
        return self.client.get_collection(
            collection_name=self.COLLECTION_NAME
        )