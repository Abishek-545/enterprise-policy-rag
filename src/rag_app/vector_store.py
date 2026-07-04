from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, MatchValue, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from rag_app.config import Settings
from rag_app.schemas import DocumentChunk, RetrievedChunk


class QdrantVectorStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.settings.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(self.settings.persist_dir))
        self.embedding_model = SentenceTransformer(self.settings.embedding_model)
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        existing = {collection.name for collection in self.client.get_collections().collections}
        if self.settings.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.settings.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def reset(self) -> None:
        existing = {collection.name for collection in self.client.get_collections().collections}
        if self.settings.collection_name in existing:
            self.client.delete_collection(self.settings.collection_name)
        self.client.create_collection(
            collection_name=self.settings.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return
        vectors = self.embedding_model.encode([chunk.text for chunk in chunks], normalize_embeddings=True)
        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(
                PointStruct(
                    id=str(uuid5(NAMESPACE_URL, chunk.id)),
                    vector=vector.tolist(),
                    payload={
                        "chunk_id": chunk.id,
                        "text": chunk.text,
                        "source": chunk.source,
                        "page": chunk.page or 0,
                        "chunk_index": chunk.chunk_index,
                    },
                )
            )
        self.client.upsert(collection_name=self.settings.collection_name, points=points)

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        vector = self.embedding_model.encode(query, normalize_embeddings=True).tolist()
        results = self.client.search(
            collection_name=self.settings.collection_name,
            query_vector=vector,
            limit=top_k,
        )
        chunks: list[RetrievedChunk] = []
        for item in results:
            payload = item.payload or {}
            chunks.append(
                RetrievedChunk(
                    id=str(payload.get("chunk_id", item.id)),
                    text=str(payload.get("text", "")),
                    source=str(payload.get("source", "unknown")),
                    page=int(payload.get("page", 0)) or None,
                    score=float(item.score),
                )
            )
        return chunks

    @property
    def persist_path(self) -> Path:
        return self.settings.persist_dir


ChromaVectorStore = QdrantVectorStore
