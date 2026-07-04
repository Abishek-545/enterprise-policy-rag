from pathlib import Path

from rag_app.chunking import chunk_file


def test_chunk_file_creates_metadata(tmp_path: Path) -> None:
    file_path = tmp_path / "policy.md"
    file_path.write_text("Remote work is allowed with manager approval. " * 80, encoding="utf-8")

    chunks = chunk_file(file_path, chunk_size=200, chunk_overlap=40)

    assert chunks
    assert chunks[0].source == "policy.md"
    assert chunks[0].chunk_index == 0
    assert "Remote work" in chunks[0].text
