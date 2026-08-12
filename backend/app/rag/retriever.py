from dataclasses import dataclass

from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    score: float
    source: str
    filename: str
    page: int | None
    chunk_index: int
    document_id: str
    document_type: str


class KnowledgeRetriever:
    def __init__(self, embeddings: EmbeddingService, store: VectorStore):
        self.embeddings, self.store = embeddings, store

    async def retrieve(self, query: str, limit: int = 5) -> list[RetrievedChunk]:
        results = await self.store.search(await self.embeddings.embed_query(query), limit)
        return [self._to_chunk(item) for item in results]

    @staticmethod
    def _to_chunk(item: dict[str, object]) -> RetrievedChunk:
        score = item.get("score")
        page = item.get("page")
        chunk_index = item.get("chunk_index")
        if not isinstance(score, int | float) or not isinstance(chunk_index, int):
            raise TypeError("Vector store returned invalid score or chunk metadata")
        if page is not None and not isinstance(page, int):
            raise TypeError("Vector store returned invalid page metadata")
        return RetrievedChunk(
            text=str(item["text"]),
            score=float(score),
            source=str(item["source"]),
            filename=str(item["filename"]),
            page=page,
            chunk_index=chunk_index,
            document_id=str(item["document_id"]),
            document_type=str(item["document_type"]),
        )
