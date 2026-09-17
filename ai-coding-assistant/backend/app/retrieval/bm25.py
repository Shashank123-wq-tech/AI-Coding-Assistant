import re

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    BM25-based lexical retrieval for repository code chunks.

    Uses code-aware tokenization so identifiers such as:

        RandomForestClassifier
        train_test_split
        roc_auc_score

    can be searched both as complete identifiers and
    as their individual components.
    """

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks or []
        self.bm25 = None

        # BM25Okapi cannot be initialized with an empty corpus.
        # Keep the retriever valid but disabled until documents exist.
        if not self.chunks:
            return

        documents = [
            chunk.get("content", "")
            for chunk in self.chunks
        ]

        tokenized_documents = [
            self._tokenize(document)
            for document in documents
        ]

        # Avoid constructing BM25 with an empty tokenized corpus.
        if not tokenized_documents:
            return

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """
        Code-aware tokenizer.

        Handles:
        - snake_case
        - camelCase
        - PascalCase
        - normal words
        - numbers inside identifiers
        """

        if not text:
            return []

        tokens = []

        raw_tokens = re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*",
            text,
        )

        for token in raw_tokens:

            token_lower = token.lower()

            # Preserve the complete identifier.
            tokens.append(token_lower)

            # Split snake_case / underscore identifiers.
            underscore_parts = [
                part
                for part in token_lower.split("_")
                if part
            ]

            tokens.extend(
                underscore_parts
            )

            # Split camelCase / PascalCase.
            camel_parts = re.findall(
                r"[A-Z]+(?=[A-Z][a-z]|\d|\b)|"
                r"[A-Z]?[a-z]+|"
                r"\d+",
                token,
            )

            tokens.extend(
                part.lower()
                for part in camel_parts
                if part.lower() != token_lower
            )

        return list(dict.fromkeys(tokens))

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict]:

        query = query.strip()

        if not query:
            return []

        if not self.chunks:
            return []

        if self.bm25 is None:
            return []

        query_tokens = self._tokenize(
            query
        )

        if not query_tokens:
            return []

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results = []

        for index in ranked_indices[:limit]:

            chunk = self.chunks[index]

            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "file_path": chunk["file_path"],
                    "chunk_type": chunk["chunk_type"],
                    "language": chunk["language"],
                    "cell_index": chunk.get(
                        "cell_index"
                    ),
                    "content": chunk["content"],
                    "metadata": chunk.get(
                        "metadata",
                        {},
                    ),
                    "score": float(
                        scores[index]
                    ),
                }
            )

        return results