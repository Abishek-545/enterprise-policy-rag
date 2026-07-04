from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def load_text_file(path: Path) -> list[tuple[str, int | None]]:
    return [(path.read_text(encoding="utf-8"), None)]


def load_pdf(path: Path) -> list[tuple[str, int | None]]:
    reader = PdfReader(str(path))
    pages: list[tuple[str, int | None]] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((text, idx))
    return pages


def load_docx(path: Path) -> list[tuple[str, int | None]]:
    document = DocxDocument(str(path))
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    return [("\n".join(paragraphs), None)]


def load_document(path: Path) -> list[tuple[str, int | None]]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix == ".docx":
        return load_docx(path)
    if suffix in {".txt", ".md"}:
        return load_text_file(path)
    raise ValueError(f"Unsupported document type: {path.suffix}")


def iter_supported_files(data_dir: Path) -> list[Path]:
    extensions = {".pdf", ".docx", ".txt", ".md"}
    return sorted(path for path in data_dir.rglob("*") if path.suffix.lower() in extensions)
