from dataclasses import dataclass, field
from typing import Any

from rag.ingestion.document_loader import LoadedDocument


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    source_file: str
    source_path: str
    title: str
    document_type: str
    content: str
    created_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 150) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be greater than or equal to zero and less than chunk_size.")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: LoadedDocument) -> list[DocumentChunk]:
        content = document.content.strip()
        if not content:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        chunk_number = 0

        while start < len(content):
            end = min(start + self.chunk_size, len(content))
            chunk_content = content[start:end].strip()
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document.document_id or document.source_file}-{chunk_number}",
                    document_id=document.document_id or document.source_file,
                    source_file=document.source_file,
                    source_path=document.source_path,
                    title=document.title,
                    document_type=document.document_type,
                    content=chunk_content,
                    created_at=document.created_at,
                    metadata={**document.metadata, "chunk_index": chunk_number},
                )
            )
            if end == len(content):
                break
            start = end - self.overlap
            chunk_number += 1

        return chunks

    def chunk_many(self, documents: list[LoadedDocument]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for document in documents:
            chunks.extend(self.chunk(document))
        return chunks
