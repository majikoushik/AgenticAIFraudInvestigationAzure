import re
from typing import Any

from rag.ingestion.document_chunker import DocumentChunk
from rag.ingestion.document_loader import LoadedDocument


class MetadataExtractor:
    def extract(self, document: LoadedDocument | DocumentChunk) -> dict[str, Any]:
        metadata = dict(document.metadata)
        metadata.setdefault("document_type", document.document_type)
        metadata.setdefault("source_file", document.source_file)
        metadata.setdefault("tags", self._tags_from_text(document.content))

        if document.document_type == "policy":
            metadata.setdefault("policy_name", document.title)
            metadata.setdefault("section_title", self._first_section(document.content) or document.title)

        if document.document_type == "historical_case":
            metadata.setdefault("case_type", "historical_fraud_case")
            metadata.setdefault("risk_indicators", metadata.get("risk_indicators", []))

        return metadata

    @staticmethod
    def _first_section(content: str) -> str | None:
        for line in content.splitlines():
            if line.startswith("## "):
                return line.lstrip("#").strip()
        return None

    @staticmethod
    def _tags_from_text(content: str) -> list[str]:
        terms = set(re.findall(r"\b(high-value|beneficiary|device|human review|policy|transfer|fraud)\b", content.lower()))
        return sorted(terms)
