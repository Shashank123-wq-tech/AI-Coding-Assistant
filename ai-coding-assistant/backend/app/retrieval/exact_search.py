from typing import Any


class ExactSearchRetriever:
    """
    Exact lexical search over indexed repository chunks.

    Designed for code identifiers, filenames, and exact phrases.
    """

    def __init__(self, chunks: list[dict[str, Any]]):
        self.chunks = chunks

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:

        query = query.strip()

        if not query or not self.chunks:
            return []

        query_lower = query.lower()

        results = []

        for chunk in self.chunks:

            content = chunk.get("content", "")
            file_path = chunk.get("file_path", "")

            content_lower = content.lower()
            file_path_lower = file_path.lower()

            score = 0
            match_type = []

            # Exact phrase in content.
            if query_lower in content_lower:
                score += 10
                match_type.append("content")

            # Exact phrase in file path.
            if query_lower in file_path_lower:
                score += 5
                match_type.append("file_path")

            if score == 0:
                continue

            results.append({
                **chunk,
                "score": score,
                "match_type": match_type,
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:limit]