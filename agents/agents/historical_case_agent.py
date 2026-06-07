import os
from pathlib import Path

from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState
from rag.retrievers.azure_historical_case_retriever import AzureHistoricalCaseRetriever
from rag.retrievers.citation_builder import build_citation
from rag.retrievers.local_historical_case_retriever import LocalHistoricalCaseRetriever


class HistoricalCaseAgent(BaseAgent):
    name = "HistoricalCaseAgent"

    def __init__(
        self,
        historical_cases_path: Path | None = None,
        azure_retriever: AzureHistoricalCaseRetriever | None = None,
        local_retriever: LocalHistoricalCaseRetriever | None = None,
    ) -> None:
        self.historical_cases_path = historical_cases_path or self._default_historical_cases_path()
        self.azure_retriever = azure_retriever or AzureHistoricalCaseRetriever()
        self.local_retriever = local_retriever or LocalHistoricalCaseRetriever(self.historical_cases_path)

    def run(self, state: InvestigationState) -> dict:
        current_codes = self._current_indicator_codes(state)
        if self._use_azure():
            query = " ".join(sorted(current_codes))
            results = self.azure_retriever.search(query, top_k=3)
            return {
                "retrieval_mode": "azure_ai_search",
                "similar_cases": [
                    {
                        "case_id": result.metadata.get("case_id", result.title),
                        "outcome": result.metadata.get("outcome", "unknown"),
                        "summary": result.content,
                        "matched_risk_indicators": result.metadata.get("risk_indicators", []),
                        "similarity_score": result.score,
                        "citation": build_citation(result),
                        "source_filename": result.source_file,
                    }
                    for result in results
                ],
                "retrieved_source_count": len({result.source_file for result in results}),
            }

        query = " ".join(sorted(current_codes))
        local_results = self.local_retriever.search(query, top_k=3)
        scored_cases = [
            {
                "case_id": result.metadata.get("case_id", result.title),
                "outcome": result.metadata.get("outcome", "unknown"),
                "summary": result.content,
                "matched_risk_indicators": sorted(current_codes.intersection(set(result.metadata.get("risk_indicators", [])))),
                "similarity_score": result.score,
                "citation": build_citation(result),
                "source_filename": result.source_file,
            }
            for result in local_results
        ]

        return {
            "retrieval_mode": "local",
            "similar_cases": scored_cases,
            "retrieved_source_count": len({case["source_filename"] for case in scored_cases}),
        }

    def _use_azure(self) -> bool:
        return os.getenv("USE_AZURE_SEARCH", "false").lower() == "true" and self.azure_retriever.is_configured

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
