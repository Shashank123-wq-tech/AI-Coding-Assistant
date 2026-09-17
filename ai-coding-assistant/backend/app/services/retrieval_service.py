from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.exact_search import ExactSearchRetriever
from app.retrieval.hybrid_search import HybridRetriever
from app.retrieval.reranker import CodeReranker
from app.retrieval.vector_search import VectorSearchRetriever


class RetrievalService:
    """
    Central repository retrieval service.

    V1:
    - Exact lexical search
    - BM25 retrieval
    - Vector semantic search
    - Hybrid retrieval using Reciprocal Rank Fusion (RRF)
    - Cross-encoder reranking
    - Target-file retrieval
    """

    def __init__(self, db: Session):
        self.db = db
        self.reranker = CodeReranker()

    def _load_chunks(
        self,
        repository_id: int,
    ) -> list[dict]:

        chunks = (
            self.db.query(CodeChunk)
            .filter(
                CodeChunk.repository_id == repository_id
            )
            .all()
        )

        return [
            {
                "chunk_id": chunk.chunk_id,
                "file_path": chunk.file_path,
                "chunk_type": chunk.chunk_type,
                "language": chunk.language,
                "cell_index": chunk.cell_index,
                "content": chunk.content,
                "metadata": chunk.chunk_metadata,
            }
            for chunk in chunks
        ]

    def search_file(
     self,
     repository_id: int,
     file_path: str,
     limit: int = 10,
     ) -> list[dict]:
      """
     Retrieve indexed chunks belonging to one target file.

    Repository isolation is enforced using repository_id.
    Path separators are normalized so Windows and POSIX paths
    match consistently.
    """
      file_path = file_path.strip()

      if not file_path:
        raise ValueError(
            "File path cannot be empty."
        )

      if limit < 1:
        raise ValueError(
            "Limit must be at least 1."
        )

      normalized_path = file_path.replace("\\", "/")

      chunks = (
        self.db.query(CodeChunk)
        .filter(
            CodeChunk.repository_id == repository_id,
        )
        .all()
        )

      results = []

      for chunk in chunks:
        chunk_path = chunk.file_path.replace("\\", "/")

        if chunk_path != normalized_path:
            continue

        results.append(
            {
                "chunk_id": chunk.chunk_id,
                "file_path": chunk.file_path,
                "chunk_type": chunk.chunk_type,
                "language": chunk.language,
                "cell_index": chunk.cell_index,
                "content": chunk.content,
                "metadata": chunk.chunk_metadata,
            }
        )

        if len(results) >= limit:
            break

        return results

    def search_exact(
        self,
        repository_id: int,
        query: str,
        limit: int = 10,
    ) -> list[dict]:

        chunks = self._load_chunks(repository_id)

        retriever = ExactSearchRetriever(chunks)

        return retriever.search(
            query=query,
            limit=limit,
        )

    def search_bm25(
        self,
        repository_id: int,
        query: str,
        limit: int = 10,
    ) -> list[dict]:

        chunks = self._load_chunks(repository_id)

        retriever = BM25Retriever(chunks)

        return retriever.search(
            query=query,
            limit=limit,
        )

    def search_hybrid(
        self,
        repository_id: int,
        query: str,
        limit: int = 10,
    ) -> list[dict]:

        chunks = self._load_chunks(repository_id)

        exact_retriever = ExactSearchRetriever(
            chunks
        )

        bm25_retriever = BM25Retriever(
            chunks
        )

        vector_retriever = VectorSearchRetriever()

        class RepositoryVectorRetriever:

            def search(
                self,
                query: str,
                limit: int = 10,
            ) -> list[dict]:

                return vector_retriever.search(
                    query=query,
                    limit=limit,
                    repository_id=repository_id,
                )

        repository_vector_retriever = (
            RepositoryVectorRetriever()
        )

        hybrid_retriever = HybridRetriever(
            retrievers={
                "exact": exact_retriever,
                "bm25": bm25_retriever,
                "vector": repository_vector_retriever,
            }
        )

        candidate_limit = max(
            limit * 2,
            10,
        )

        candidates = hybrid_retriever.search(
            query=query,
            limit=candidate_limit,
        )

        reranked_results = self.reranker.rerank(
            query=query,
            results=candidates,
            limit=limit,
        )

        return reranked_results

    def search(
        self,
        repository_id: int,
        query: str,
        limit: int = 10,
        method: str = "bm25",
    ) -> list[dict]:

        if method == "exact":
            return self.search_exact(
                repository_id=repository_id,
                query=query,
                limit=limit,
            )

        if method == "bm25":
            return self.search_bm25(
                repository_id=repository_id,
                query=query,
                limit=limit,
            )

        if method == "hybrid":
            return self.search_hybrid(
                repository_id=repository_id,
                query=query,
                limit=limit,
            )

        raise ValueError(
            f"Unsupported retrieval method: {method}"
        )