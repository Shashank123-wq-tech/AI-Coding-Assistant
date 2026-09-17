from sqlalchemy.orm import Session

from app.agents.context_builder import RAGContextBuilder
from app.services.retrieval_service import RetrievalService
from app.llm.groq_provider import GroqProvider


class RepositoryQAService:
    """
    Repository question-answering service.

    Retrieves relevant repository context, builds a grounded prompt,
    and generates an answer using the configured LLM provider.
    """

    def __init__(self, db: Session):
        self.db = db

        self.retrieval_service = RetrievalService(
            db=db
        )

        self.context_builder = RAGContextBuilder()

        self.llm_provider = GroqProvider()

    def _build_prompt(
        self,
        query: str,
        context: str,
    ) -> str:

        return f"""
You are an AI coding assistant answering questions about a software repository.

Answer the user's question using ONLY the repository context provided below.

Rules:
1. Do not invent code, files, functions, classes, or behavior.
2. If the context does not contain enough information, explicitly say so.
3. Explain the answer clearly and concisely.
4. When possible, mention the relevant file and notebook cell.
5. Do not claim that code exists if it is not present in the context.

USER QUESTION
=============

{query}

{context}

ANSWER
======
""".strip()

    def answer(
        self,
        repository_id: int,
        query: str,
        limit: int = 5,
    ) -> dict:

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        results = self.retrieval_service.search(
            repository_id=repository_id,
            query=query,
            limit=limit,
            method="hybrid",
        )

        context = self.context_builder.build(
            query=query,
            results=results,
        )

        prompt = self._build_prompt(
            query=query,
            context=context,
        )

        answer = self.llm_provider.generate(
            prompt
        )

        return {
            "repository_id": repository_id,
            "query": query,
            "retrieval_method": "hybrid",
            "retrieved_chunks": len(results),
            "answer": answer,
            "sources": [
                {
                    "chunk_id": result.get("chunk_id"),
                    "file_path": result.get("file_path"),
                    "chunk_type": result.get("chunk_type"),
                    "cell_index": result.get("cell_index"),
                    "reranker_score": result.get(
                        "reranker_score"
                    ),
                }
                for result in results
            ],
        }