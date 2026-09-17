from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generate vector embeddings for code and text.

    V1 uses:
        BAAI/bge-small-en-v1.5
    """

    MODEL_NAME = "BAAI/bge-small-en-v1.5"

    def __init__(self):
        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

    def embed(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        vector = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return vector.tolist()

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            return []

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return vectors.tolist()