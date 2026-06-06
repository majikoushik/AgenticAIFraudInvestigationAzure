from rag.ingestion.document_chunker import DocumentChunker
from rag.ingestion.document_loader import LoadedDocument


def test_document_chunker_preserves_metadata_and_overlap() -> None:
    document = LoadedDocument(
        source_file="policy.md",
        title="Policy",
        document_type="policy",
        content="abcdefghijklmnopqrstuvwxyz",
        metadata={"policy_name": "Policy"},
    )
    chunker = DocumentChunker(chunk_size=10, overlap=3)

    chunks = chunker.chunk(document)

    assert len(chunks) == 4
    assert chunks[0].content == "abcdefghij"
    assert chunks[1].content.startswith("hij")
    assert chunks[0].source_file == "policy.md"
    assert chunks[0].metadata["policy_name"] == "Policy"
