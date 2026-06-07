from rag.ingestion.document_loader import DocumentLoader, LoadedDocument


class PdfLoader:
    def load(self, path: str) -> LoadedDocument:
        return DocumentLoader().load_pdf_file(path)
