from collections import defaultdict
from typing import Any


class HybridRetriever:
    def __init__(
        self,
        retrievers: dict[str, Any],
        rrf_k: int = 60,
    ):
        self.retrievers = retrievers
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        query = query.strip()

        if not query:
            return []

        fused_scores = defaultdict(float)
        result_data = {}

        for method_name, retriever in self.retrievers.items():
            results = retriever.search(
                query=query,
                limit=limit,
            )

            for rank, result in enumerate(results, start=1):
                # Ignore zero/negative lexical scores.
                # Vector similarity scores are normally positive,
                # so they remain eligible.
                if (
                    method_name in {"exact", "bm25"}
                    and result.get("score", 0) <= 0
                ):
                    continue

                chunk_id = result["chunk_id"]

                # Reciprocal Rank Fusion
                fused_scores[chunk_id] += (
                    1.0 / (self.rrf_k + rank)
                )

                # Preserve the result metadata.
                if chunk_id not in result_data:
                    result_data[chunk_id] = dict(result)

                # Keep individual retrieval scores for debugging.
                result_data[chunk_id].setdefault(
                    "retrieval_scores",
                    {},
                )

                result_data[chunk_id]["retrieval_scores"][
                    method_name
                ] = result.get("score")

        ranked_chunk_ids = sorted(
            fused_scores,
            key=lambda chunk_id: fused_scores[chunk_id],
            reverse=True,
        )

        final_results = []

        for chunk_id in ranked_chunk_ids[:limit]:
            result = dict(result_data[chunk_id])

            result["rrf_score"] = fused_scores[chunk_id]

            final_results.append(result)

        return final_results