from rag.ingestion.document_loader import DocumentLoader, LoadedDocument


class MarkdownLoader:
    def load(self, path: str) -> LoadedDocument:
        return DocumentLoader().load_markdown_file(path)
