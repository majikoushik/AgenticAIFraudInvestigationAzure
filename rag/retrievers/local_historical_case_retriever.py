import json
import re
from pathlib import Path

from rag.retrievers.base_retriever import RetrievalResult


class LocalHistoricalCaseRetriever:
    retrieval_mode = "local"

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).resolve().parents[2] / "data" / "synthetic" / "historical_cases.json"

    def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[RetrievalResult]:
        terms = self._tokens(query)
        results = []
        if not self.path.exists():
            return []
        for record in json.loads(self.path.read_text(encoding="utf-8")):
            text = " ".join([record.get("summary", ""), " ".join(record.get("risk_indicators", [])), record.get("outcome", "")])
            score = len(terms.intersection(self._tokens(text)))
            if score:
                results.append(RetrievalResult(
                    id=record.get("case_id", ""),
                    title=record.get("case_id", "Historical case"),
                    content=record.get("summary", ""),
                    source_file=self.path.name,
                    source_path=str(self.path),
                    document_type="HISTORICAL_CASE",
                    score=float(score),
                    metadata={**record, "retrieval_mode": "local"},
                ))
        return sorted(results, key=lambda result: result.score, reverse=True)[:top_k]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}
