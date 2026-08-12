from pathlib import Path

from app.rag.loaders import load_text
from app.rag.splitter import split_text


def prepare_document(path: Path) -> list[str]:
    return split_text(load_text(path))
