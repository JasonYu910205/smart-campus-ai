from dataclasses import dataclass

from app.rag.retriever import KnowledgeRetriever, RetrievedChunk
from app.services.llm import LLMService

SYSTEM_PROMPT = """You are the SmartCampus maintenance knowledge assistant.

Answer the user's question only using the supplied knowledge base context.

Rules:
1. Do not invent device procedures.
2. If the answer cannot be supported by the supplied context, explicitly say the knowledge base does not contain enough information.
3. Prioritize safety instructions.
4. Never recommend bypassing safety protection.
5. Include concise troubleshooting steps.
6. Every factual answer must include source citations using the supplied labels."""


@dataclass(frozen=True)
class SourceCitation:
    filename: str
    page: int | None
    chunk_index: int
    score: float


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    sources: list[SourceCitation]


def map_citations(chunks: list[RetrievedChunk]) -> list[SourceCitation]:
    return [
        SourceCitation(chunk.filename, chunk.page, chunk.chunk_index, chunk.score)
        for chunk in chunks
    ]


class BasicRagChain:
    def __init__(self, retriever: KnowledgeRetriever, llm: LLMService, top_k: int = 5):
        self.retriever, self.llm, self.top_k = retriever, llm, top_k

    async def ask(self, question: str) -> RagAnswer:
        chunks = await self.retriever.retrieve(question, self.top_k)
        context = "\n\n".join(
            f"[Source {index}: {chunk.filename}, page={chunk.page}, chunk={chunk.chunk_index}]\n"
            f"{chunk.text}"
            for index, chunk in enumerate(chunks, start=1)
        )
        prompt = f"Knowledge base context:\n{context}\n\nUser question: {question}"
        answer = await self.llm.generate(SYSTEM_PROMPT, prompt)
        return RagAnswer(answer, map_citations(chunks))
