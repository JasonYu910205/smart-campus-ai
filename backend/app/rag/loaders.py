from pathlib import Path


def load_text(path: Path) -> str:
    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("V0.1 supports TXT and Markdown only")
    return path.read_text(encoding="utf-8")
