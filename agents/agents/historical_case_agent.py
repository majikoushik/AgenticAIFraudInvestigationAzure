import os
from pathlib import Path

from agents.agents.base_agent import BaseAgent
from agents.observability.rag_telemetry import track_rag_event
from agents.orchestration.state_manager import InvestigationState
from app.observability import telemetry_events
from rag.retrievers.azure_historical_case_retriever import AzureHistoricalCaseRetriever
from rag.retrievers.citation_builder import build_citation
from rag.retrievers.local_historical_case_retriever import LocalHistoricalCaseRetriever
from time import perf_counter


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
        case_id = state.case.get("metadata", {}).get("case_id")
        if self._use_azure():
            query = " ".join(sorted(current_codes))
            started = perf_counter()
            track_rag_event(telemetry_events.RAG_RETRIEVAL_STARTED, {"case_id": case_id, "retrieval_mode": "azure_ai_search", "index_name": "historical_cases", "top_k": 3})
            results = self.azure_retriever.search(query, top_k=3)
            latency_ms = round((perf_counter() - started) * 1000, 2)
            track_rag_event(telemetry_events.RAG_RETRIEVAL_COMPLETED, {"case_id": case_id, "retrieval_mode": "azure_ai_search", "index_name": "historical_cases", "result_count": len(results), "source_count": len({result.source_file for result in results})}, {"retrieval_latency_ms": latency_ms})
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
        started = perf_counter()
        track_rag_event(telemetry_events.RAG_RETRIEVAL_STARTED, {"case_id": case_id, "retrieval_mode": "local", "index_name": "historical_cases", "top_k": 3})
        local_results = self.local_retriever.search(query, top_k=3)
        latency_ms = round((perf_counter() - started) * 1000, 2)
        track_rag_event(telemetry_events.RAG_RETRIEVAL_COMPLETED, {"case_id": case_id, "retrieval_mode": "local", "index_name": "historical_cases", "result_count": len(local_results), "source_count": len({result.source_file for result in local_results})}, {"retrieval_latency_ms": latency_ms})
        if not local_results:
            track_rag_event(telemetry_events.RAG_EMPTY_RESULT, {"case_id": case_id, "retrieval_mode": "local", "index_name": "historical_cases"})
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
