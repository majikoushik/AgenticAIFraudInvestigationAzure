from rag.ingestion.document_loader import DocumentLoader, LoadedDocument


class JsonLoader:
    def load(self, path: str, document_type: str = "HISTORICAL_CASE") -> list[LoadedDocument]:
        return DocumentLoader().load_json_file(path, document_type)
