import logging

from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def service_health(session: AsyncSession) -> dict[str, str]:
    settings = get_settings()
    status = {
        "status": "ok",
        "postgres": "error",
        "qdrant": "error",
        "redis": "error",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
    }
    try:
        await session.execute(text("SELECT 1"))
        status["postgres"] = "ok"
    except Exception as exc:  # Service probes must report degraded instead of failing the endpoint.
        logger.warning("PostgreSQL health check failed: %s", exc)
    redis = Redis.from_url(settings.redis_url)
    try:
        if await redis.ping():
            status["redis"] = "ok"
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
    finally:
        await redis.aclose()
    client = AsyncQdrantClient(url=settings.qdrant_url)
    try:
        await client.get_collections()
        status["qdrant"] = "ok"
    except Exception as exc:
        logger.warning("Qdrant health check failed: %s", exc)
    finally:
        await client.close()
    if "error" in status.values():
        status["status"] = "degraded"
    return status
