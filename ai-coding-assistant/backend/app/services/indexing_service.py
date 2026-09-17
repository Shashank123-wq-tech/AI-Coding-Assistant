from sqlalchemy.orm import Session

from app.code_intelligence.code_indexer import CodeIndexer
from app.models.code_chunk import CodeChunk
from app.models.repository import Repository


class IndexingService:
    """
    Convert repository source code into searchable chunks
    and persist them in PostgreSQL.
    """

    def __init__(self, db: Session):
        self.db = db

    def index_repository(self, repository: Repository) -> dict:
        indexer = CodeIndexer(repository.local_path)

        result = indexer.index()
        chunks = result["chunks"]

        # Remove previous chunks for this repository.
        self.db.query(CodeChunk).filter(
            CodeChunk.repository_id == repository.id
        ).delete(
            synchronize_session=False
        )

        inserted = 0

        for chunk in chunks:
            code_chunk = CodeChunk(
                repository_id=repository.id,
                chunk_id=chunk["chunk_id"],
                file_path=chunk["file_path"],
                chunk_type=chunk["chunk_type"],
                language=chunk["language"],
                cell_index=chunk.get("cell_index"),
                content=chunk["content"],
                chunk_metadata=chunk.get("metadata", {}),
            )

            self.db.add(code_chunk)
            inserted += 1

        repository.status = "indexed"

        self.db.commit()

        return {
            "repository_id": repository.id,
            "repository": repository.name,
            "total_chunks": inserted,
            "status": "indexed",
        }