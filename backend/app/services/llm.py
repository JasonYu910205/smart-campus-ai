from typing import Protocol

import httpx

from app.core.config import Settings


class LLMService(Protocol):
    provider: str
    model: str

    async def generate(self, system_prompt: str, user_prompt: str) -> str: ...


class OpenAICompatibleLLMService:
    """Adapter for cloud or private OpenAI-compatible generation endpoints."""

    def __init__(
        self,
        settings: Settings,
        client: httpx.AsyncClient | None = None,
        *,
        require_api_key: bool,
    ):
        api_key = settings.llm_api_key.get_secret_value()
        if not settings.llm_model or not settings.llm_base_url:
            raise ValueError("LLM_BASE_URL and LLM_MODEL are required")
        if require_api_key and not api_key:
            raise ValueError("LLM_API_KEY is required for this provider")
        self.provider = settings.llm_provider.lower().strip()
        self.model = settings.llm_model
        self.endpoint = f"{settings.llm_base_url.rstrip('/')}/chat/completions"
        self.client = client or httpx.AsyncClient(timeout=90)
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.post(
            self.endpoint,
            headers=self.headers,
            json={
                "model": self.model,
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"])


def create_llm_service(settings: Settings, client: httpx.AsyncClient | None = None) -> LLMService:
    provider = settings.llm_provider.lower().strip()
    if provider in {"deepseek", "openai_compatible"}:
        return OpenAICompatibleLLMService(settings, client, require_api_key=True)
    if provider in {"local", "private"}:
        return OpenAICompatibleLLMService(settings, client, require_api_key=False)
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
