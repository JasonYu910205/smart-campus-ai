import hashlib
import uuid
from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document

from app.rag.embeddings import EmbeddingService
from app.rag.loaders import load_documents
from app.rag.splitter import split_documents
from app.rag.vector_store import VectorStore


@dataclass(frozen=True)
class IngestionResult:
    document_id: str
    filename: str
    chunks_count: int
    vector_dimension: int
    status: str = "indexed"


def deterministic_document_id(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{path.name}:{digest}"))


def prepare_document(
    path: Path, chunk_size: int = 600, overlap: int = 100
) -> tuple[str, list[Document]]:
    document_id = deterministic_document_id(path)
    return document_id, split_documents(load_documents(path), document_id, chunk_size, overlap)


class DocumentIngestionService:
    def __init__(
        self,
        embeddings: EmbeddingService,
        store: VectorStore,
        chunk_size: int = 600,
        chunk_overlap: int = 100,
    ):
        self.embeddings = embeddings
        self.store = store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def ingest(self, path: Path) -> IngestionResult:
        document_id = deterministic_document_id(path)
        chunks = split_documents(
            load_documents(path), document_id, self.chunk_size, self.chunk_overlap
        )
        vectors = await self.embeddings.embed_documents([chunk.page_content for chunk in chunks])
        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}:{index}"))
            for index in range(len(chunks))
        ]
        payloads = [{**chunk.metadata, "text": chunk.page_content} for chunk in chunks]
        await self.store.upsert(ids, vectors, payloads)
        dimension = len(vectors[0]) if vectors else 0
        return IngestionResult(document_id, path.name, len(chunks), dimension)
