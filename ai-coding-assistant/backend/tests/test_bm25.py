from app.retrieval.bm25 import BM25Retriever


def test_empty_corpus_does_not_crash():
    retriever = BM25Retriever([])

    assert retriever.bm25 is None
    assert retriever.search("calculator") == []


def test_bm25_search_returns_matching_chunk():
    chunks = [
        {
            "chunk_id": "chunk-1",
            "file_path": "calculator.py",
            "chunk_type": "function",
            "language": "python",
            "cell_index": None,
            "content": "def add(a, b): return a + b",
            "metadata": {},
        },
        {
            "chunk_id": "chunk-2",
            "file_path": "calculator.py",
            "chunk_type": "function",
            "language": "python",
            "cell_index": None,
            "content": "def multiply(a, b): return a * b",
            "metadata": {},
        },
    ]

    retriever = BM25Retriever(chunks)

    results = retriever.search("add", limit=1)

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"