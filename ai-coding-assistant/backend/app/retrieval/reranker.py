from typing import Any

from sentence_transformers import CrossEncoder


class CodeReranker:
    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self):
        self.model = CrossEncoder(self.MODEL_NAME)

    def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        query = query.strip()

        if not query or not results or limit < 1:
            return []

        pairs = [
            (
                query,
                result.get("content", ""),
            )
            for result in results
        ]

        scores = self.model.predict(pairs)

        reranked_results = []

        for result, score in zip(results, scores):
            reranked_result = dict(result)
            reranked_result["reranker_score"] = float(score)
            reranked_results.append(reranked_result)

        reranked_results.sort(
            key=lambda result: result["reranker_score"],
            reverse=True,
        )

        return reranked_results[:limit]