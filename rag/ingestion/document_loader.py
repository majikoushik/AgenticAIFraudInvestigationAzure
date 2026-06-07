import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LoadedDocument:
    source_file: str
    title: str
    document_type: str
    content: str
    document_id: str = ""
    source_path: str = ""
    loaded_at: str = ""
    created_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentLoader:
    def load_path(self, path: str | Path, document_type: str = "POLICY") -> LoadedDocument | None:
        file_path = Path(path)
        try:
            if file_path.suffix.lower() == ".md":
                return self.load_markdown_file(file_path, document_type)
            if file_path.suffix.lower() == ".txt":
                return self.load_text_file(file_path, document_type)
            if file_path.suffix.lower() == ".json":
                documents = self.load_json_file(file_path, document_type)
                return documents[0] if documents else None
            if file_path.suffix.lower() == ".pdf":
                return self.load_pdf_file(file_path, document_type)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            return None
        return None

    def load_directory(self, directory: str | Path, document_type: str = "POLICY") -> list[LoadedDocument]:
        documents: list[LoadedDocument] = []
        for path in sorted(Path(directory).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".json", ".pdf"}:
                continue
            loaded = self.load_json_file(path, document_type) if path.suffix.lower() == ".json" else [self.load_path(path, document_type)]
            documents.extend(document for document in loaded if document and document.content.strip())
        return documents

    def load_markdown_directory(self, directory: str | Path) -> list[LoadedDocument]:
        return [document for document in (self.load_markdown_file(path) for path in sorted(Path(directory).glob("*.md"))) if document.content.strip()]

    def load_markdown_file(self, path: str | Path, document_type: str = "POLICY") -> LoadedDocument:
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8")
        title = self._first_markdown_heading(content) or file_path.stem.replace("-", " ").title()
        return self._build_document(file_path, title, document_type, content, {"policy_name": title})

    def load_text_file(self, path: str | Path, document_type: str = "SOP") -> LoadedDocument:
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8")
        return self._build_document(file_path, file_path.stem.replace("-", " ").title(), document_type, content, {})

    def load_pdf_file(self, path: str | Path, document_type: str = "POLICY") -> LoadedDocument:
        file_path = Path(path)
        try:
            from pypdf import PdfReader
            content = "\n".join(page.extract_text() or "" for page in PdfReader(str(file_path)).pages)
        except Exception as exc:
            raise ValueError(f"PDF extraction failed for {file_path.name}: {exc}") from exc
        return self._build_document(file_path, file_path.stem.replace("-", " ").title(), document_type, content, {})

    def load_json_file(self, path: str | Path, document_type: str = "HISTORICAL_CASE") -> list[LoadedDocument]:
        file_path = Path(path)
        data = json.loads(file_path.read_text(encoding="utf-8"))
        records = data if isinstance(data, list) else [data]
        documents: list[LoadedDocument] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            title = record.get("title") or record.get("case_id") or record.get("historical_case_id") or f"{file_path.stem}-{index}"
            content = self._json_record_to_text(record)
            if content.strip():
                documents.append(self._build_document(file_path, str(title), document_type, content, dict(record)))
        return documents

    def load_historical_cases(self, path: str | Path) -> list[LoadedDocument]:
        return self.load_json_file(path, "HISTORICAL_CASE")

    def _build_document(self, file_path: Path, title: str, document_type: str, content: str, metadata: dict[str, Any]) -> LoadedDocument:
        source_path = str(file_path)
        document_id = metadata.get("document_id") or hashlib.sha1(f"{source_path}:{title}".encode("utf-8")).hexdigest()[:16]
        loaded_at = datetime.now(UTC).isoformat()
        return LoadedDocument(
            document_id=document_id,
            source_file=file_path.name,
            source_path=source_path,
            title=title,
            document_type=document_type.upper(),
            content=content,
            created_at=metadata.get("created_at") or datetime.fromtimestamp(file_path.stat().st_mtime, UTC).isoformat(),
            loaded_at=loaded_at,
            metadata={**metadata, "source_path": source_path},
        )

    @staticmethod
    def _first_markdown_heading(content: str) -> str | None:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.lstrip("#").strip()
        return None

    @staticmethod
    def _json_record_to_text(record: dict[str, Any]) -> str:
        parts = []
        for key, value in record.items():
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                value = json.dumps(value, sort_keys=True)
            parts.append(f"{key}: {value}")
        return "\n".join(parts)
