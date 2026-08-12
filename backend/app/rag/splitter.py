from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents: list[Document], document_id: str, chunk_size: int = 600, overlap: int = 100
) -> list[Document]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must exceed overlap")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", "；", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata = {**chunk.metadata, "document_id": document_id, "chunk_index": index}
    return chunks


def split_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    document = Document(page_content=text, metadata={})
    return [
        chunk.page_content for chunk in split_documents([document], "inline", chunk_size, overlap)
    ]
