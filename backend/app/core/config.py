from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SmartCampus AI Copilot"
    database_url: str = (
        "postgresql+asyncpg://smart_campus:smart_campus_dev@postgres:5432/smart_campus"
    )
    qdrant_url: str = "http://qdrant:6333"
    redis_url: str = "redis://redis:6379/0"
    backend_cors_origins: str = "http://localhost:3000"
    llm_provider: str = "deepseek"
    llm_api_key: SecretStr = SecretStr("")
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = ""
    embedding_provider: str = "qwen"
    embedding_api_key: SecretStr = SecretStr("")
    embedding_base_url: str = ""
    embedding_model: str = ""
    qdrant_collection: str = "smart_campus_knowledge"
    rag_chunk_size: int = 600
    rag_chunk_overlap: int = 100
    rag_top_k: int = 5
    rag_max_upload_bytes: int = 10 * 1024 * 1024
    knowledge_upload_dir: str = "/tmp/smart-campus-uploads"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.backend_cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
