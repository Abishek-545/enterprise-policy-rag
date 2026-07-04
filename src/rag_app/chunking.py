from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_app.loaders import load_document
from rag_app.schemas import DocumentChunk


def chunk_file(path: Path, chunk_size: int, chunk_overlap: int) -> list[DocumentChunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks: list[DocumentChunk] = []
    for text, page in load_document(path):
        for idx, chunk_text in enumerate(splitter.split_text(text)):
            clean_text = " ".join(chunk_text.split())
            if not clean_text:
                continue
            chunk_id = f"{path.stem}-p{page or 0}-c{idx}"
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    text=clean_text,
                    source=path.name,
                    page=page,
                    chunk_index=idx,
                )
            )
    return chunks
