from pathlib import Path

import pytest

from app.rag.loaders import load_text
from app.rag.splitter import split_text


def test_splitter_overlap() -> None:
    assert split_text("abcdefghij", 6, 2) == ["abcdef", "efghij", "ij"]


def test_loader_rejects_pdf(tmp_path: Path) -> None:
    path = tmp_path / "manual.pdf"
    path.write_bytes(b"pdf")
    with pytest.raises(ValueError):
        load_text(path)
