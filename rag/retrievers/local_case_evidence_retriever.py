import json
import re
from pathlib import Path
from typing import Any

from rag.retrievers.base_retriever import RetrievalResult


class LocalCaseEvidenceRetriever:
    retrieval_mode = "local"

    def __init__(self, synthetic_data_directory: Path | None = None) -> None:
        self.synthetic_data_directory = synthetic_data_directory or self._default_data_directory()

    def search(self, query: str, top_k: int = 3, filters: dict | None = None) -> list[RetrievalResult]:
        query_terms = self._tokenize(query)
        records = self._load_evidence_records()
        results: list[RetrievalResult] = []

        for record in records:
            if not self._matches_filters(record["payload"], filters or {}):
                continue
            searchable = self._record_to_text(record["payload"])
            score = len(query_terms.intersection(self._tokenize(searchable)))
            if score <= 0:
                continue

            results.append(
                RetrievalResult(
                    id=record["id"],
                    title=record["title"],
                    content=self._shorten(searchable),
                    source_file=record["source_file"],
                    source_path=str(record["source_path"]),
                    document_type="CASE_EVIDENCE",
                    score=float(score),
                    metadata={
                        "document_type": "CASE_EVIDENCE",
                        "evidence_type": record["evidence_type"],
                        "case_id": record["payload"].get("case_id") or record["payload"].get("alert_id"),
                        "customer_id": record["payload"].get("customer_id"),
                        "retrieval_mode": self.retrieval_mode,
                    },
                )
            )

        return sorted(results, key=lambda result: result.score, reverse=True)[:top_k]

    def _load_evidence_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for filename in ["fraud_alerts.json", "transactions.json", "beneficiaries.json", "devices.json", "customers.json"]:
            path = self.synthetic_data_directory / filename
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            items = payload if isinstance(payload, list) else [payload]
            for index, item in enumerate(items):
                if isinstance(item, dict):
                    records.append(
                        {
                            "id": str(item.get("case_id") or item.get("alert_id") or item.get("transaction_id") or item.get("id") or index),
                            "title": self._title_for_record(filename, item),
                            "source_file": filename,
                            "source_path": path,
                            "evidence_type": filename.removesuffix(".json"),
                            "payload": item,
                        }
                    )
        return records

    @staticmethod
    def _matches_filters(item: dict[str, Any], filters: dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if expected is None:
                continue
            if str(item.get(key, "")).lower() != str(expected).lower():
                return False
        return True

    @staticmethod
    def _title_for_record(filename: str, item: dict[str, Any]) -> str:
        identifier = item.get("case_id") or item.get("alert_id") or item.get("transaction_id") or item.get("customer_id") or item.get("id")
        return f"{filename.removesuffix('.json')} {identifier}".strip()

    @staticmethod
    def _record_to_text(item: dict[str, Any]) -> str:
        parts: list[str] = []
        for key, value in item.items():
            if isinstance(value, (dict, list)):
                value_text = json.dumps(value, ensure_ascii=True)
            else:
                value_text = str(value)
            parts.append(f"{key}: {value_text}")
        return " ".join(parts)

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}

    @staticmethod
    def _shorten(text: str, limit: int = 360) -> str:
        return text if len(text) <= limit else f"{text[:limit].rstrip()}..."

    @staticmethod
    def _default_data_directory() -> Path:
        return Path(__file__).resolve().parents[2] / "data" / "synthetic"
