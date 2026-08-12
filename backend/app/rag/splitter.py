def split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must exceed overlap")
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]
