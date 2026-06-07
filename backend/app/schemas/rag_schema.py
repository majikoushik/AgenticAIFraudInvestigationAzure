from typing import Any

from pydantic import BaseModel, Field


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)
    case_id: str | None = None
    filters: dict[str, Any] | None = None


class RagRetrievalResult(BaseModel):
    title: str
    source_filename: str
    source_path: str = ""
    matched_section: str
    snippet: str
    score: float = 0.0
    reranker_score: float = 0.0
    retrieval_mode: str
    citation: dict[str, Any]
    chunk_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    explanation: str | None = None


class PolicySearchResponse(BaseModel):
    query: str
    retrieval_mode: str
    results: list[RagRetrievalResult]


class RagSearchResponse(BaseModel):
    query: str
    retrieval_mode: str
    index_type: str
    results: list[RagRetrievalResult]


class RagSearchAllResponse(BaseModel):
    query: str
    retrieval_mode: str
    policies: list[RagRetrievalResult]
    historical_cases: list[RagRetrievalResult]
    case_evidence: list[RagRetrievalResult]


class RagHealthResponse(BaseModel):
    status: str
    retrieval_mode: str
    azure_search_configured: bool
    azure_embeddings_configured: bool
    indexes: dict[str, str]
