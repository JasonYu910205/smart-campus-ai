import json

import httpx
import pytest

from app.core.config import Settings
from app.rag.embeddings import OpenAICompatibleEmbeddingService, create_embedding_service
from app.services.llm import OpenAICompatibleLLMService, create_llm_service


def settings() -> Settings:
    return Settings(
        llm_provider="deepseek",
        llm_api_key="llm-secret",
        llm_base_url="https://llm.example/v1",
        llm_model="deepseek-chat",
        embedding_provider="qwen",
        embedding_api_key="embedding-secret",
        embedding_base_url="https://embedding.example/v1",
        embedding_model="text-embedding-v3",
    )


def test_provider_factories_use_independent_configuration() -> None:
    config = settings()
    llm = create_llm_service(config)
    embeddings = create_embedding_service(config)
    assert isinstance(llm, OpenAICompatibleLLMService)
    assert isinstance(embeddings, OpenAICompatibleEmbeddingService)
    assert llm.headers["Authorization"] == "Bearer llm-secret"
    assert embeddings.headers["Authorization"] == "Bearer embedding-secret"
    assert "embedding-secret" not in json.dumps(llm.headers)
    assert "llm-secret" not in json.dumps(embeddings.headers)


def test_unknown_providers_are_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        create_llm_service(settings().model_copy(update={"llm_provider": "unknown"}))
    with pytest.raises(ValueError, match="Unsupported embedding provider"):
        create_embedding_service(settings().model_copy(update={"embedding_provider": "unknown"}))


def test_local_private_providers_do_not_require_cloud_keys() -> None:
    config = Settings(
        llm_provider="local",
        llm_api_key="",
        llm_base_url="http://private-llm:8000/v1",
        llm_model="private-chat",
        embedding_provider="private",
        embedding_api_key="",
        embedding_base_url="http://private-embedding:8001/v1",
        embedding_model="private-embedding",
    )
    llm = create_llm_service(config)
    embeddings = create_embedding_service(config)
    assert llm.provider == "local"
    assert embeddings.provider == "private"
    assert llm.headers == {}
    assert embeddings.headers == {}


@pytest.mark.asyncio
async def test_services_send_only_their_own_credentials() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/embeddings"):
            return httpx.Response(200, json={"data": [{"index": 0, "embedding": [1, 2]}]})
        return httpx.Response(200, json={"choices": [{"message": {"content": "grounded answer"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    config = settings()
    embeddings = create_embedding_service(config, client)
    llm = create_llm_service(config, client)
    assert await embeddings.embed_query("query") == [1.0, 2.0]
    assert await llm.generate("system", "question") == "grounded answer"
    assert requests[0].headers["authorization"] == "Bearer embedding-secret"
    assert requests[1].headers["authorization"] == "Bearer llm-secret"
    await client.aclose()


def test_settings_repr_does_not_expose_keys() -> None:
    assert "llm-secret" not in repr(settings())
    assert "embedding-secret" not in repr(settings())
