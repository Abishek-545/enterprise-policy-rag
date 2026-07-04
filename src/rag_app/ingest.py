from pathlib import Path

from rag_app.chunking import chunk_file
from rag_app.config import get_settings
from rag_app.loaders import iter_supported_files
from rag_app.schemas import IngestionResult
from rag_app.vector_store import ChromaVectorStore


def ingest_directory(data_dir: Path, reset: bool = True) -> IngestionResult:
    settings = get_settings()
    store = ChromaVectorStore(settings)
    if reset:
        store.reset()

    files = iter_supported_files(data_dir)
    all_chunks = []
    for file_path in files:
        all_chunks.extend(chunk_file(file_path, settings.chunk_size, settings.chunk_overlap))

    store.add_chunks(all_chunks)
    return IngestionResult(
        files_processed=len(files),
        chunks_created=len(all_chunks),
        vector_store_path=store.persist_path,
    )


if __name__ == "__main__":
    result = ingest_directory(Path("data/sample_docs"), reset=True)
    print(
        f"Processed {result.files_processed} files, created {result.chunks_created} chunks, "
        f"stored vectors at {result.vector_store_path}"
    )
