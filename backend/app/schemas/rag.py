from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunkRead(BaseModel):
    text: str
    score: float
    source: str
    filename: str
    page: int | None
    chunk_index: int
    document_id: str
    document_type: str


class RetrievalResponse(BaseModel):
    embedding_provider: str
    embedding_model: str
    query: str
    top_k: int
    chunks: list[RetrievedChunkRead]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class SourceRead(BaseModel):
    filename: str
    page: int | None
    chunk_index: int
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceRead]


class IngestionResponse(BaseModel):
    document_id: str
    filename: str
    chunks_count: int
    vector_dimension: int
    status: str
