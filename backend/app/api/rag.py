import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.rag.dependencies import build_components
from app.rag.loaders import SUPPORTED_EXTENSIONS
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    IngestionResponse,
    RetrievalRequest,
    RetrievalResponse,
    RetrievedChunkRead,
)

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


def _configuration_error(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=503, detail=str(exc))


@router.post("/knowledge/documents", response_model=IngestionResponse)
async def upload_document(file: Annotated[UploadFile, File()]) -> IngestionResponse:
    settings = get_settings()
    filename = Path(file.filename or "upload").name
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Only .md, .txt, and .pdf files are supported")
    content = await file.read(settings.rag_max_upload_bytes + 1)
    if len(content) > settings.rag_max_upload_bytes:
        raise HTTPException(status_code=413, detail="Document exceeds the upload size limit")
    upload_dir = Path(settings.knowledge_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / filename
    path.write_bytes(content)
    try:
        ingestion, _, _, store = build_components()
        result = await ingestion.ingest(path)
        await store.close()
    except ValueError as exc:
        raise _configuration_error(exc) from exc
    except Exception as exc:
        logger.exception("Document ingestion failed for %s", filename)
        raise HTTPException(status_code=502, detail="Document indexing failed") from exc
    return IngestionResponse(**result.__dict__)


@router.post("/rag/retrieve", response_model=RetrievalResponse)
async def retrieve(request: RetrievalRequest) -> RetrievalResponse:
    settings = get_settings()
    try:
        _, retriever, _, store = build_components()
        chunks = await retriever.retrieve(request.query, request.top_k)
        await store.close()
    except ValueError as exc:
        raise _configuration_error(exc) from exc
    return RetrievalResponse(
        embedding_provider=settings.embedding_provider,
        embedding_model=settings.embedding_model,
        query=request.query,
        top_k=request.top_k,
        chunks=[RetrievedChunkRead(**chunk.__dict__) for chunk in chunks],
    )


@router.post("/rag/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    try:
        _, _, chain, store = build_components()
        result = await chain.ask(request.question)
        await store.close()
    except ValueError as exc:
        raise _configuration_error(exc) from exc
    return AskResponse(
        answer=result.answer,
        sources=[source.__dict__ for source in result.sources],
    )
