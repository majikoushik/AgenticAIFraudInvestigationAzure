import json
import time
from dataclasses import asdict
from pathlib import Path

from rag.ingestion.azure_search_uploader import AzureSearchUploader
from rag.ingestion.document_chunker import DocumentChunker
from rag.ingestion.document_loader import DocumentLoader
from rag.ingestion.embedding_generator import EmbeddingGenerator
from rag.ingestion.metadata_extractor import MetadataExtractor


class IngestionPipeline:
    def __init__(self) -> None:
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.metadata_extractor = MetadataExtractor()
        self.embedding_generator = EmbeddingGenerator()
        self.uploader = AzureSearchUploader()

    def run(self, input_folder: str | Path, document_type: str, index_name: str) -> dict:
        started = time.perf_counter()
        documents = self.loader.load_directory(input_folder, document_type)
        chunks = self.chunker.chunk_many(documents)
        upload_docs = []
        for chunk in chunks:
            metadata = self.metadata_extractor.extract(chunk)
            embedding = self.embedding_generator.generate_embedding(chunk.content)
            upload_docs.append({
                "id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "content": chunk.content,
                "source_file": chunk.source_file,
                "source_path": chunk.source_path,
                "document_type": chunk.document_type,
                "content_vector": embedding,
                "created_at": chunk.created_at,
                "metadata_json": json.dumps(metadata, sort_keys=True),
                **{key: value for key, value in metadata.items() if isinstance(value, (str, list))},
            })
        upload = self.uploader.upload_chunks(index_name, upload_docs) if upload_docs else {"chunks_uploaded": 0, "chunks_failed": 0}
        return {
            "documents_loaded": len(documents),
            "documents_failed": 0,
            "chunks_created": len(chunks),
            **upload,
            "embedding_enabled": self.embedding_generator.is_available(),
            "index_name": index_name,
            "duration_seconds": round(time.perf_counter() - started, 2),
        }
