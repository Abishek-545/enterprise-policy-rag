from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    text: str
    source: str
    page: int | None
    chunk_index: int


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    text: str
    source: str
    page: int | None
    score: float


@dataclass(frozen=True)
class IngestionResult:
    files_processed: int
    chunks_created: int
    vector_store_path: Path
