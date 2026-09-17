from qdrant_client.models import PointStruct
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.models.repository import Repository
from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.qdrant_service import QdrantService


class VectorIndexingService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def index_repository(self, repository: Repository) -> dict:
        chunks = (
            self.db.query(CodeChunk)
            .filter(CodeChunk.repository_id == repository.id)
            .all()
        )

        if not chunks:
            return {
                "repository_id": repository.id,
                "total_chunks": 0,
                "status": "no_chunks",
            }

        self.qdrant_service.create_collection()

        texts = [chunk.content for chunk in chunks]

        vectors = self.embedding_service.embed_batch(texts)

        points = []

        for chunk, vector in zip(chunks, vectors):
            points.append(
                PointStruct(
                    id=chunk.id,
                    vector=vector,
                    payload={
                        "repository_id": chunk.repository_id,
                        "chunk_id": chunk.chunk_id,
                        "file_path": chunk.file_path,
                        "chunk_type": chunk.chunk_type,
                        "language": chunk.language,
                        "cell_index": chunk.cell_index,
                        "content": chunk.content,
                        "metadata": chunk.chunk_metadata,
                    },
                )
            )

        self.qdrant_service.client.upsert(
            collection_name=self.qdrant_service.COLLECTION_NAME,
            points=points,
        )

        return {
            "repository_id": repository.id,
            "total_chunks": len(points),
            "status": "vector_indexed",
        }