from pathlib import Path

import pytest
from langchain_core.documents import Document

from app.rag.chain import BasicRagChain, map_citations
from app.rag.ingestion import DocumentIngestionService, deterministic_document_id
from app.rag.loaders import load_documents
from app.rag.retriever import KnowledgeRetriever, RetrievedChunk
from app.rag.splitter import split_documents, split_text


class FakeEmbeddings:
    provider = "fake"
    model = "fake-embedding"

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), 1.0] for text in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [float(len(text)), 1.0]


class FakeStore:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] = []

    async def upsert(
        self, ids: list[str], vectors: list[list[float]], metadata: list[dict[str, object]]
    ) -> None:
        self.payloads = metadata

    async def search(self, vector: list[float], limit: int = 5) -> list[dict[str, object]]:
        return [
            {
                "text": "E03 表示冷藏室温度异常报警。",
                "score": 0.93,
                "source": "/knowledge/manual.md",
                "filename": "manual.md",
                "page": None,
                "chunk_index": 2,
                "document_id": "doc-1",
                "document_type": "md",
            }
        ][:limit]


class FakeLLM:
    provider = "fake"
    model = "fake-llm"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        assert "E03 表示" in user_prompt
        return "E03 是温度异常报警。[Source 1]"


def test_markdown_loader_metadata(tmp_path: Path) -> None:
    path = tmp_path / "manual.md"
    path.write_text("# 冷藏柜手册\nE03 故障", encoding="utf-8")
    documents = load_documents(path)
    assert documents[0].page_content.startswith("# 冷藏柜手册")
    assert documents[0].metadata == {
        "source": str(path),
        "filename": "manual.md",
        "document_type": "md",
        "page": None,
        "title": "manual",
    }


def test_loader_rejects_unknown_type(tmp_path: Path) -> None:
    path = tmp_path / "manual.docx"
    path.write_bytes(b"document")
    with pytest.raises(ValueError):
        load_documents(path)


def test_chunking_and_metadata_preservation() -> None:
    document = Document(page_content="A" * 900, metadata={"source": "manual.md", "page": None})
    chunks = split_documents([document], "document-1", chunk_size=600, overlap=100)
    assert len(chunks) == 2
    assert chunks[0].metadata["source"] == "manual.md"
    assert chunks[1].metadata["document_id"] == "document-1"
    assert chunks[1].metadata["chunk_index"] == 1
    assert split_text("短文本") == ["短文本"]


@pytest.mark.asyncio
async def test_ingestion_is_deterministic(tmp_path: Path) -> None:
    path = tmp_path / "manual.md"
    path.write_text("# 手册\n" + "E03 温度异常。" * 100, encoding="utf-8")
    store = FakeStore()
    service = DocumentIngestionService(FakeEmbeddings(), store)
    first = await service.ingest(path)
    second = await service.ingest(path)
    assert first.document_id == second.document_id == deterministic_document_id(path)
    assert all(payload["document_id"] == first.document_id for payload in store.payloads)


@pytest.mark.asyncio
async def test_retriever_returns_typed_chunks() -> None:
    chunks = await KnowledgeRetriever(FakeEmbeddings(), FakeStore()).retrieve("E03", 5)
    assert chunks[0].filename == "manual.md"
    assert chunks[0].score == pytest.approx(0.93)


@pytest.mark.asyncio
async def test_citation_mapping_comes_from_retriever() -> None:
    retriever = KnowledgeRetriever(FakeEmbeddings(), FakeStore())
    result = await BasicRagChain(retriever, FakeLLM()).ask("E03 怎么处理？")
    assert result.sources == map_citations(await retriever.retrieve("E03 怎么处理？"))
    assert result.sources[0].filename == "manual.md"
    assert result.sources[0].chunk_index == 2


def test_map_citations_preserves_metadata() -> None:
    chunks = [RetrievedChunk("text", 0.88, "source", "sop.md", 3, 4, "id", "md")]
    citation = map_citations(chunks)[0]
    assert (citation.filename, citation.page, citation.chunk_index, citation.score) == (
        "sop.md",
        3,
        4,
        0.88,
    )
