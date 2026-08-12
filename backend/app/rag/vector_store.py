from typing import Protocol


class VectorStore(Protocol):
    async def upsert(
        self, ids: list[str], vectors: list[list[float]], metadata: list[dict[str, object]]
    ) -> None: ...
    async def search(self, vector: list[float], limit: int = 5) -> list[dict[str, object]]: ...
