from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class RetrievalResult:
    title: str
    content: str
    source_file: str
    id: str = ""
    source_path: str = ""
    document_type: str = "POLICY"
    score: float = 0.0
    reranker_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    citation: dict[str, Any] = field(default_factory=dict)


class Retriever(Protocol):
    retrieval_mode: str

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        ...
