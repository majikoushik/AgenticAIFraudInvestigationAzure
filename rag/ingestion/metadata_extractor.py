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

        doc_type = document.document_type.upper()
        if doc_type == "POLICY":
            metadata.setdefault("policy_name", document.title)
            metadata.setdefault("section_title", self._first_section(document.content) or document.title)
            metadata.setdefault("policy_version", metadata.get("version"))
            metadata.setdefault("effective_date", metadata.get("effective_date"))

        if doc_type == "HISTORICAL_CASE":
            metadata.setdefault("historical_case_id", metadata.get("case_id") or metadata.get("historical_case_id"))
            metadata.setdefault("case_type", metadata.get("case_type", "historical_fraud_case"))
            metadata.setdefault("risk_indicators", metadata.get("risk_indicators", []))
            metadata.setdefault("outcome", metadata.get("outcome", "unknown"))
            metadata.setdefault("channel", metadata.get("channel"))
            metadata.setdefault("amount_band", metadata.get("amount_band"))
            metadata.setdefault("customer_segment", metadata.get("customer_segment"))

        if doc_type in {"SOP", "REGULATORY"}:
            metadata.setdefault("regulation_name", metadata.get("regulation_name") or document.title)
            metadata.setdefault("region", metadata.get("region"))
            metadata.setdefault("section_title", self._first_section(document.content) or document.title)
            metadata.setdefault("topic", metadata.get("topic"))

        if doc_type == "CASE_EVIDENCE":
            metadata.setdefault("case_id", metadata.get("case_id"))
            metadata.setdefault("evidence_type", metadata.get("evidence_type"))
            metadata.setdefault("evidence_source", metadata.get("evidence_source") or document.source_file)
            metadata.setdefault("created_by", metadata.get("created_by"))

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
