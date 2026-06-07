from rag.ingestion.document_loader import DocumentLoader, LoadedDocument


class TextLoader:
    def load(self, path: str) -> LoadedDocument:
        return DocumentLoader().load_text_file(path)
