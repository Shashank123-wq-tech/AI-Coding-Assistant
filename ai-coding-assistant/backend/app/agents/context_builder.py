from typing import Any


class RAGContextBuilder:
    """
    Builds grounded context from retrieved repository chunks.

    The context is deliberately structured so the LLM can distinguish
    repository evidence from the user's question.
    """

    def __init__(
        self,
        max_chunks: int = 5,
        max_chars_per_chunk: int = 6000,
    ):
        self.max_chunks = max_chunks
        self.max_chars_per_chunk = max_chars_per_chunk

    def build(
        self,
        query: str,
        results: list[dict[str, Any]],
    ) -> str:
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        if not results:
            return (
                "No relevant repository context was retrieved "
                "for this question."
            )

        selected_results = results[: self.max_chunks]

        context_parts = [
            "REPOSITORY CONTEXT",
            "==================",
            "",
        ]

        for index, result in enumerate(
            selected_results,
            start=1,
        ):
            file_path = result.get(
                "file_path",
                "unknown",
            )

            chunk_id = result.get(
                "chunk_id",
                "unknown",
            )

            chunk_type = result.get(
                "chunk_type",
                "unknown",
            )

            language = result.get(
                "language",
                "unknown",
            )

            cell_index = result.get(
                "cell_index",
            )

            content = result.get(
                "content",
                "",
            )

            content = content[: self.max_chars_per_chunk]

            context_parts.append(
                f"[Context {index}]"
            )

            context_parts.append(
                f"File: {file_path}"
            )

            context_parts.append(
                f"Chunk ID: {chunk_id}"
            )

            context_parts.append(
                f"Type: {chunk_type}"
            )

            context_parts.append(
                f"Language: {language}"
            )

            if cell_index is not None:
                context_parts.append(
                    f"Notebook Cell: {cell_index}"
                )

            context_parts.append("Code/Content:")

            context_parts.append(
                "```text"
            )

            context_parts.append(
                content
            )

            context_parts.append(
                "```"
            )

            context_parts.append("")

        context_parts.append(
            "END REPOSITORY CONTEXT"
        )

        return "\n".join(context_parts)