from agents.agents.base_agent import BaseAgent
from agents.observability.rag_telemetry import track_rag_event
from agents.orchestration.state_manager import InvestigationState
from app.core.constants import AuditEventType
from app.observability import telemetry_events
from app.services.audit_service import audit_service
from rag.retrievers.citation_builder import build_policy_reference
from rag.retrievers.hybrid_retriever import HybridPolicyRetriever
from time import perf_counter


class PolicyRagAgent(BaseAgent):
    name = "PolicyRagAgent"

    def __init__(self, retriever: HybridPolicyRetriever | None = None) -> None:
        self.retriever = retriever or HybridPolicyRetriever()

    def run(self, state: InvestigationState) -> dict:
        query = self._build_query(state)
        case_id = state.case.get("metadata", {}).get("case_id")
        audit_service.create_rag_retrieval_event(
            case_id=case_id,
            event_type=AuditEventType.RAG_RETRIEVAL_STARTED,
            rag_query=query,
            metadata={"top_k": 3},
        )
        try:
            started = perf_counter()
            track_rag_event(telemetry_events.RAG_RETRIEVAL_STARTED, {"case_id": case_id, "retrieval_mode": self.retriever.retrieval_mode, "index_name": "policies", "top_k": 3})
            matches = self.retriever.search(query, top_k=3)
        except Exception as exc:
            track_rag_event(telemetry_events.RAG_RETRIEVAL_FAILED, {"case_id": case_id, "retrieval_mode": self.retriever.retrieval_mode, "index_name": "policies", "error_type": type(exc).__name__})
            audit_service.create_rag_retrieval_event(
                case_id=case_id,
                event_type=AuditEventType.RAG_RETRIEVAL_FAILED,
                rag_query=query,
                error_message=str(exc),
            )
            raise
        references = [build_policy_reference(match) for match in matches]
        retrieval_latency_ms = round((perf_counter() - started) * 1000, 2)
        source_count = len({reference["source_filename"] for reference in references})
        citation_count = len([reference for reference in references if reference.get("citation")])
        track_rag_event(
            telemetry_events.RAG_RETRIEVAL_COMPLETED,
            {
                "case_id": case_id,
                "retrieval_mode": self.retriever.retrieval_mode,
                "index_name": "policies",
                "result_count": len(references),
                "source_count": source_count,
                "top_sources": [reference["source_filename"] for reference in references],
                "citation_count": citation_count,
                "citation_valid": citation_count == len(references),
            },
            {"retrieval_latency_ms": retrieval_latency_ms},
        )
        if not references:
            track_rag_event(telemetry_events.RAG_EMPTY_RESULT, {"case_id": case_id, "retrieval_mode": self.retriever.retrieval_mode, "index_name": "policies"})
        audit_service.create_rag_retrieval_event(
            case_id=case_id,
            event_type=AuditEventType.RAG_RETRIEVAL_COMPLETED,
            rag_query=query,
            rag_sources=[reference["source_filename"] for reference in references],
            metadata={"result_count": len(references), "retrieval_mode": self.retriever.retrieval_mode},
        )

        return {
            "query": query,
            "retrieval_mode": self.retriever.retrieval_mode,
            "policy_references": references,
            "retrieved_source_count": source_count,
            "citation_count": citation_count,
            "top_sources": [reference["source_filename"] for reference in references],
            "message": "" if references else "No matching policy snippets were retrieved for this case.",
        }

    @staticmethod
    def _build_query(state: InvestigationState) -> str:
        indicator_codes = [
            indicator["code"].replace("_", " ")
            for output in state.outputs.values()
            for indicator in output.get("risk_indicators", [])
        ]
        reason = state.case["metadata"]["reason"]
        channel = state.case["suspicious_transaction"]["channel"]
        return " ".join([reason, channel, *indicator_codes])
