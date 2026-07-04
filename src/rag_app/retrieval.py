import re

from rank_bm25 import BM25Okapi

from rag_app.schemas import RetrievedChunk
from rag_app.vector_store import ChromaVectorStore

_TOKEN_PATTERN = re.compile(r"\w+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text.lower())


class HybridRetriever:
    """Combines semantic retrieval with BM25 lexical scoring."""

    def __init__(self, store: ChromaVectorStore):
        self.store = store

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        semantic_results = self.store.search(query, top_k=max(top_k * 4, 10))
        if not semantic_results:
            return []

        corpus_tokens = [_tokenize(chunk.text) for chunk in semantic_results]
        bm25 = BM25Okapi(corpus_tokens)
        bm25_scores = bm25.get_scores(_tokenize(query))
        max_bm25 = max(bm25_scores) if len(bm25_scores) else 0.0

        fused: list[RetrievedChunk] = []
        for chunk, bm25_score in zip(semantic_results, bm25_scores):
            lexical = float(bm25_score / max_bm25) if max_bm25 else 0.0
            hybrid_score = (0.75 * chunk.score) + (0.25 * lexical)
            fused.append(
                RetrievedChunk(
                    id=chunk.id,
                    text=chunk.text,
                    source=chunk.source,
                    page=chunk.page,
                    score=hybrid_score,
                )
            )

        return sorted(fused, key=lambda item: item.score, reverse=True)[:top_k]
