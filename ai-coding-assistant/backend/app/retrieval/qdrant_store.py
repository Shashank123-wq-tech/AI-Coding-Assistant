from qdrant_client import QdrantClient


class QdrantStore:

    def __init__(
        self,
        url: str,
    ):

        self.client = QdrantClient(
            url=url
        )


    def collections(self):

        return self.client.get_collections()
