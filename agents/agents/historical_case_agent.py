import json
import os
from pathlib import Path

from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState
from rag.retrievers.azure_historical_case_retriever import AzureHistoricalCaseRetriever


class HistoricalCaseAgent(BaseAgent):
    name = "HistoricalCaseAgent"

    def __init__(
        self,
        historical_cases_path: Path | None = None,
        azure_retriever: AzureHistoricalCaseRetriever | None = None,
    ) -> None:
        self.historical_cases_path = historical_cases_path or self._default_historical_cases_path()
        self.azure_retriever = azure_retriever or AzureHistoricalCaseRetriever()

    def run(self, state: InvestigationState) -> dict:
        current_codes = self._current_indicator_codes(state)
        if self._use_azure():
            query = " ".join(sorted(current_codes))
            results = self.azure_retriever.search(query, top_k=3)
            return {
                "retrieval_mode": "azure_search",
                "similar_cases": [
                    {
                        "case_id": result.metadata.get("case_id", result.title),
                        "outcome": result.metadata.get("outcome", "unknown"),
                        "summary": result.content,
                        "matched_risk_indicators": result.metadata.get("risk_indicators", []),
                        "similarity_score": result.score,
                    }
                    for result in results
                ],
            }

        cases = self._load_cases()
        scored_cases = []

        for historical_case in cases:
            historical_codes = set(historical_case.get("risk_indicators", []))
            overlap = sorted(current_codes.intersection(historical_codes))
            if overlap:
                scored_cases.append(
                    {
                        "case_id": historical_case["case_id"],
                        "outcome": historical_case["outcome"],
                        "summary": historical_case["summary"],
                        "matched_risk_indicators": overlap,
                        "similarity_score": len(overlap),
                    }
                )

        return {
            "retrieval_mode": "local",
            "similar_cases": sorted(
                scored_cases,
                key=lambda case: case["similarity_score"],
                reverse=True,
            )[:3]
        }

    def _use_azure(self) -> bool:
        return os.getenv("USE_AZURE_SEARCH", "false").lower() == "true" and self.azure_retriever.is_configured

    def _load_cases(self) -> list[dict]:
        with self.historical_cases_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _current_indicator_codes(state: InvestigationState) -> set[str]:
        return {
            indicator["code"]
            for output in state.outputs.values()
            for indicator in output.get("risk_indicators", [])
        }

    @staticmethod
    def _default_historical_cases_path() -> Path:
        return Path(__file__).resolve().parents[2] / "data" / "synthetic" / "historical_cases.json"
