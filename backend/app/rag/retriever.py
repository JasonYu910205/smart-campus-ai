from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore


class KnowledgeRetriever:
    def __init__(self, embeddings: EmbeddingService, store: VectorStore):
        self.embeddings, self.store = embeddings, store

    async def retrieve(self, query: str, limit: int = 5) -> list[dict[str, object]]:
        return await self.store.search(await self.embeddings.embed_query(query), limit)
