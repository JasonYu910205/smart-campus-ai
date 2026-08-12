import asyncio
import logging
from pathlib import Path

from app.core.config import get_settings
from app.rag.dependencies import build_components
from app.rag.loaders import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


async def seed_knowledge() -> None:
    settings = get_settings()
    root = Path(__file__).resolve().parents[3] / "data" / "documents"
    ingestion, _, _, store = build_components()
    documents_count = 0
    chunks_count = 0
    vector_dimension = 0
    logger.info("Embedding Provider: %s", settings.embedding_provider)
    logger.info("Embedding Model: %s", settings.embedding_model)
    logger.info("Qdrant Collection: %s", settings.qdrant_collection)
    try:
        for path in sorted(root.iterdir()):
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            result = await ingestion.ingest(path)
            documents_count += 1
            chunks_count += result.chunks_count
            vector_dimension = result.vector_dimension
            logger.info("Indexed %s (%s chunks)", result.filename, result.chunks_count)
    finally:
        await store.close()
    logger.info("Vector Dimension: %s", vector_dimension)
    logger.info("Documents: %s", documents_count)
    logger.info("Chunks: %s", chunks_count)
    logger.info("Points Upserted: %s", chunks_count)


if __name__ == "__main__":
    asyncio.run(seed_knowledge())
