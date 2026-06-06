from pathlib import Path

from rag.ingestion.document_chunker import DocumentChunker
from rag.ingestion.document_loader import DocumentLoader
from rag.ingestion.embedding_generator import EmbeddingGenerator
from rag.ingestion.metadata_extractor import MetadataExtractor
from rag.ingestion.search_index_uploader import SearchIndexUploader


def main() -> None:
    index_name = __import__("os").getenv("AZURE_SEARCH_POLICY_INDEX", "fraud-policies")
    policy_dir = Path(__file__).resolve().parents[1] / "sample_documents" / "policies"
    loader = DocumentLoader()
    chunker = DocumentChunker()
    metadata_extractor = MetadataExtractor()
    embedding_generator = EmbeddingGenerator()
    uploader = SearchIndexUploader()

    documents = loader.load_markdown_directory(policy_dir)
    chunks = chunker.chunk_many(documents)
    upload_documents = []

    for chunk in chunks:
        metadata = metadata_extractor.extract(chunk)
        vector = embedding_generator.generate(chunk.content) if embedding_generator.is_configured else []
        upload_documents.append(
            {
                "id": chunk.chunk_id,
                "title": chunk.title,
                "content": chunk.content,
                "source_file": chunk.source_file,
                "document_type": chunk.document_type,
                "policy_name": metadata.get("policy_name", chunk.title),
                "section_title": metadata.get("section_title", chunk.title),
                "tags": metadata.get("tags", []),
                "content_vector": vector,
                "created_at": chunk.created_at,
            }
        )

    if not embedding_generator.is_configured:
        print("Warning: Azure OpenAI embeddings are not configured. Uploading empty vectors.")

    result = uploader.upload_documents(index_name, upload_documents)
    print(f"Uploaded {len(upload_documents)} policy chunks to {index_name}: {result}")


if __name__ == "__main__":
    main()
