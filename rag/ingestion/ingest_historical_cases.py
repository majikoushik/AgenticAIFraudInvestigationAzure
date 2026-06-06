from pathlib import Path
import os

from rag.ingestion.document_chunker import DocumentChunker
from rag.ingestion.document_loader import DocumentLoader
from rag.ingestion.embedding_generator import EmbeddingGenerator
from rag.ingestion.metadata_extractor import MetadataExtractor
from rag.ingestion.search_index_uploader import SearchIndexUploader


def main() -> None:
    index_name = os.getenv("AZURE_SEARCH_CASE_INDEX", "historical-fraud-cases")
    cases_path = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "historical_cases.json"
    loader = DocumentLoader()
    chunker = DocumentChunker()
    metadata_extractor = MetadataExtractor()
    embedding_generator = EmbeddingGenerator()
    uploader = SearchIndexUploader()

    chunks = chunker.chunk_many(loader.load_historical_cases(cases_path))
    upload_documents = []

    for chunk in chunks:
        metadata = metadata_extractor.extract(chunk)
        vector = embedding_generator.generate(chunk.content) if embedding_generator.is_configured else []
        upload_documents.append(
            {
                "id": chunk.chunk_id,
                "case_id": metadata.get("case_id", chunk.chunk_id),
                "title": chunk.title,
                "content": chunk.content,
                "source_file": chunk.source_file,
                "case_type": metadata.get("case_type", "historical_fraud_case"),
                "risk_indicators": metadata.get("risk_indicators", []),
                "outcome": metadata.get("outcome", "unknown"),
                "content_vector": vector,
                "created_at": chunk.created_at,
            }
        )

    if not embedding_generator.is_configured:
        print("Warning: Azure OpenAI embeddings are not configured. Uploading empty vectors.")

    result = uploader.upload_documents(index_name, upload_documents)
    print(f"Uploaded {len(upload_documents)} historical case chunks to {index_name}: {result}")


if __name__ == "__main__":
    main()
