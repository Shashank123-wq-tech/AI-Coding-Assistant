from typing import Any

from app.agents.context_builder import RAGContextBuilder
from app.llm.groq_provider import GroqProvider
from app.services.retrieval_service import RetrievalService


class CodingAgent:
    """
    Coding agent responsible for understanding a coding request
    using repository context.

    V1 does not modify files or execute commands.
    It only analyzes the request and produces a structured plan.
    """

    def __init__(self, db):
        self.db = db

        self.retrieval_service = RetrievalService(
            db=db
        )

        self.context_builder = RAGContextBuilder(
            max_chunks=8,
            max_chars_per_chunk=6000,
        )

        self.llm_provider = GroqProvider()

    def _build_prompt(
        self,
        request: str,
        context: str,
    ) -> str:

        return f"""
You are an AI coding agent working on a software repository.

Your task is to analyze the user's coding request and determine
what changes would be required.

IMPORTANT RULES:

1. Use only the repository context provided below.
2. Do not invent files, functions, classes, or behavior.
3. Do not modify files.
4. Do not execute commands.
5. Do not claim that a file needs modification unless the
   repository context provides evidence.
6. Identify the relevant files and explain why they are relevant.
7. If the repository context is insufficient, explicitly say so.
8. Produce a concise implementation plan.

USER CODING REQUEST
===================

{request}

{context}

RETURN YOUR RESPONSE IN THIS STRUCTURE:

SUMMARY:
<short description>

RELEVANT FILES:
- <file>: <reason>

IMPLEMENTATION PLAN:
1. <step>
2. <step>
3. <step>

RISKS OR CONSIDERATIONS:
- <item>

MISSING INFORMATION:
- <item>
""".strip()

    def analyze(
        self,
        repository_id: int,
        request: str,
        limit: int = 8,
    ) -> dict[str, Any]:

        request = request.strip()

        if not request:
            raise ValueError(
                "Coding request cannot be empty."
            )

        results = self.retrieval_service.search(
            repository_id=repository_id,
            query=request,
            limit=limit,
            method="hybrid",
        )

        context = self.context_builder.build(
            query=request,
            results=results,
        )

        prompt = self._build_prompt(
            request=request,
            context=context,
        )

        analysis = self.llm_provider.generate(
            prompt
        )

        return {
            "repository_id": repository_id,
            "request": request,
            "retrieval_method": "hybrid",
            "retrieved_chunks": len(results),
            "analysis": analysis,
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