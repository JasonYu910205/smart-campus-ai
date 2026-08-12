from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


def _base_metadata(path: Path) -> dict[str, str | int | None]:
    extension = path.suffix.lower()
    return {
        "source": str(path),
        "filename": path.name,
        "document_type": extension.removeprefix("."),
        "page": None,
        "title": path.stem.replace("_", " ").strip(),
    }


def load_documents(path: Path) -> list[Document]:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only Markdown, TXT, and PDF documents are supported")
    metadata = _base_metadata(path)
    if extension != ".pdf":
        return [Document(page_content=path.read_text(encoding="utf-8"), metadata=metadata)]

    documents: list[Document] = []
    for page_number, page in enumerate(PdfReader(path).pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(
                Document(page_content=text, metadata={**metadata, "page": page_number})
            )
    if not documents:
        raise ValueError("The PDF does not contain extractable text")
    return documents


def load_text(path: Path) -> str:
    """Compatibility helper for callers that only need combined text."""
    return "\n\n".join(document.page_content for document in load_documents(path))
