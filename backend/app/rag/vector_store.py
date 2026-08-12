from typing import Protocol

from qdrant_client import AsyncQdrantClient, models


class VectorStore(Protocol):
    async def upsert(
        self, ids: list[str], vectors: list[list[float]], metadata: list[dict[str, object]]
    ) -> None: ...
    async def search(self, vector: list[float], limit: int = 5) -> list[dict[str, object]]: ...


class QdrantVectorStore:
    def __init__(self, url: str, collection: str):
        self.client = AsyncQdrantClient(url=url)
        self.collection = collection

    async def ensure_collection(self, vector_size: int) -> None:
        if not await self.client.collection_exists(self.collection):
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=models.Distance.COSINE
                ),
            )
            return
        info = await self.client.get_collection(self.collection)
        vectors = info.config.params.vectors
        existing_size = vectors.size if isinstance(vectors, models.VectorParams) else None
        if existing_size != vector_size:
            raise ValueError(
                f"Embedding dimension {vector_size} does not match collection dimension "
                f"{existing_size}"
            )

    async def upsert(
        self, ids: list[str], vectors: list[list[float]], metadata: list[dict[str, object]]
    ) -> None:
        if not vectors:
            return
        await self.ensure_collection(len(vectors[0]))
        await self.client.upsert(
            collection_name=self.collection,
            points=[
                models.PointStruct(id=point_id, vector=vector, payload=payload)
                for point_id, vector, payload in zip(ids, vectors, metadata, strict=True)
            ],
            wait=True,
        )

    async def search(self, vector: list[float], limit: int = 5) -> list[dict[str, object]]:
        await self.ensure_collection(len(vector))
        result = await self.client.query_points(
            collection_name=self.collection, query=vector, limit=limit, with_payload=True
        )
        return [{**(point.payload or {}), "score": float(point.score)} for point in result.points]

    async def close(self) -> None:
        await self.client.close()
