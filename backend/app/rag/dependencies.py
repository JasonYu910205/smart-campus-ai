from app.core.config import get_settings
from app.rag.chain import BasicRagChain
from app.rag.embeddings import create_embedding_service
from app.rag.ingestion import DocumentIngestionService
from app.rag.retriever import KnowledgeRetriever
from app.rag.vector_store import QdrantVectorStore
from app.services.llm import create_llm_service


def build_components() -> tuple[
    DocumentIngestionService, KnowledgeRetriever, BasicRagChain, QdrantVectorStore
]:
    settings = get_settings()
    embeddings = create_embedding_service(settings)
    store = QdrantVectorStore(settings.qdrant_url, settings.qdrant_collection)
    retriever = KnowledgeRetriever(embeddings, store)
    ingestion = DocumentIngestionService(
        embeddings, store, settings.rag_chunk_size, settings.rag_chunk_overlap
    )
    chain = BasicRagChain(retriever, create_llm_service(settings), settings.rag_top_k)
    return ingestion, retriever, chain, store
