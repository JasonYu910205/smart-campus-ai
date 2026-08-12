from typing import Protocol

import httpx

from app.core.config import Settings


class EmbeddingService(Protocol):
    provider: str
    model: str

    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_query(self, text: str) -> list[float]: ...


class OpenAICompatibleEmbeddingService:
    """Adapter for cloud or private OpenAI-compatible embedding endpoints."""

    def __init__(
        self,
        settings: Settings,
        client: httpx.AsyncClient | None = None,
        *,
        require_api_key: bool,
    ):
        api_key = settings.embedding_api_key.get_secret_value()
        if not settings.embedding_model or not settings.embedding_base_url:
            raise ValueError("EMBEDDING_BASE_URL and EMBEDDING_MODEL are required")
        if require_api_key and not api_key:
            raise ValueError("EMBEDDING_API_KEY is required for this provider")
        self.provider = settings.embedding_provider.lower().strip()
        self.model = settings.embedding_model
        self.endpoint = f"{settings.embedding_base_url.rstrip('/')}/embeddings"
        self.client = client or httpx.AsyncClient(timeout=60)
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.post(
            self.endpoint, headers=self.headers, json={"model": self.model, "input": texts}
        )
        response.raise_for_status()
        payload = response.json()
        ordered = sorted(payload["data"], key=lambda item: item["index"])
        return [[float(value) for value in item["embedding"]] for item in ordered]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._embed(texts)

    async def embed_query(self, text: str) -> list[float]:
        return (await self._embed([text]))[0]


def create_embedding_service(
    settings: Settings, client: httpx.AsyncClient | None = None
) -> EmbeddingService:
    provider = settings.embedding_provider.lower().strip()
    if provider in {"qwen", "openai_compatible"}:
        return OpenAICompatibleEmbeddingService(settings, client, require_api_key=True)
    if provider in {"local", "private"}:
        return OpenAICompatibleEmbeddingService(settings, client, require_api_key=False)
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
