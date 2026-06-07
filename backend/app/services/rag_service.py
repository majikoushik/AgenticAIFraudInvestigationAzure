from pathlib import Path
import sys

from app.core.constants import AuditEventType
from app.schemas.rag_schema import RagHealthResponse, RagSearchAllResponse, RagSearchResponse, PolicySearchResponse
from app.services.audit_service import AuditService


def _ensure_project_root_on_path() -> None:
    project_root = Path(__file__).resolve().parents[3]
    project_root_text = str(project_root)
    if project_root_text not in sys.path:
        sys.path.append(project_root_text)


_ensure_project_root_on_path()

from rag.config.index_config import index_names  # noqa: E402
from rag.config.rag_config import RagConfig  # noqa: E402
from rag.ingestion.embedding_generator import EmbeddingGenerator  # noqa: E402
from rag.retrievers.azure_case_evidence_retriever import AzureCaseEvidenceRetriever  # noqa: E402
from rag.retrievers.citation_builder import build_citation, build_policy_reference  # noqa: E402
from rag.retrievers.hybrid_retriever import HybridPolicyRetriever  # noqa: E402
from rag.retrievers.local_case_evidence_retriever import LocalCaseEvidenceRetriever  # noqa: E402
from rag.retrievers.local_historical_case_retriever import LocalHistoricalCaseRetriever  # noqa: E402
from rag.retrievers.azure_historical_case_retriever import AzureHistoricalCaseRetriever  # noqa: E402


class RagService:
    def __init__(
        self,
        policy_retriever: HybridPolicyRetriever | None = None,
        historical_retriever: LocalHistoricalCaseRetriever | AzureHistoricalCaseRetriever | None = None,
        evidence_retriever: LocalCaseEvidenceRetriever | AzureCaseEvidenceRetriever | None = None,
        audit_service: AuditService | None = None,
        config: RagConfig | None = None,
    ) -> None:
        self.config = config or RagConfig()
        self.policy_retriever = policy_retriever or HybridPolicyRetriever()
        self.historical_retriever = historical_retriever or self._default_historical_retriever()
        self.evidence_retriever = evidence_retriever or self._default_evidence_retriever()
        self.audit_service = audit_service or AuditService()

    def search_policies(self, query: str, top_k: int = 3, case_id: str | None = None) -> PolicySearchResponse:
        results = self.policy_retriever.search(query, top_k=top_k)
        self._record_retrieval(query, "policy", results, case_id)
        return PolicySearchResponse(
            query=query,
            retrieval_mode=self.policy_retriever.retrieval_mode,
            results=[build_policy_reference(result) for result in results],
        )

    def search_historical_cases(
        self,
        query: str,
        top_k: int = 3,
        case_id: str | None = None,
        filters: dict | None = None,
    ) -> RagSearchResponse:
        results = self.historical_retriever.search(query, top_k=top_k, filters=filters)
        self._record_retrieval(query, "historical_case", results, case_id)
        return RagSearchResponse(
            query=query,
            retrieval_mode=self.historical_retriever.retrieval_mode,
            index_type="historical_cases",
            results=[build_citation(result) for result in results],
        )

    def search_case_evidence(
        self,
        query: str,
        top_k: int = 3,
        case_id: str | None = None,
        filters: dict | None = None,
    ) -> RagSearchResponse:
        if case_id:
            filters = {**(filters or {}), "case_id": case_id}
        results = self.evidence_retriever.search(query, top_k=top_k, filters=filters)
        self._record_retrieval(query, "case_evidence", results, case_id)
        return RagSearchResponse(
            query=query,
            retrieval_mode=self.evidence_retriever.retrieval_mode,
            index_type="case_evidence",
            results=[build_citation(result) for result in results],
        )

    def search_all(self, query: str, top_k: int = 3, case_id: str | None = None) -> RagSearchAllResponse:
        policies = self.policy_retriever.search(query, top_k=top_k)
        historical_cases = self.historical_retriever.search(query, top_k=top_k)
        evidence_filters = {"case_id": case_id} if case_id else None
        case_evidence = self.evidence_retriever.search(query, top_k=top_k, filters=evidence_filters)
        self._record_retrieval(query, "all", [*policies, *historical_cases, *case_evidence], case_id)
        return RagSearchAllResponse(
            query=query,
            retrieval_mode=self._combined_mode(),
            policies=[build_policy_reference(result) for result in policies],
            historical_cases=[build_citation(result) for result in historical_cases],
            case_evidence=[build_citation(result) for result in case_evidence],
        )

    def get_health(self) -> RagHealthResponse:
        configured_indexes = index_names()
        return RagHealthResponse(
            status="ok",
            retrieval_mode=self._combined_mode(),
            azure_search_configured=self.config.azure_search_configured,
            azure_embeddings_configured=EmbeddingGenerator().is_available(),
            indexes={
                "policies": configured_indexes["policy_index"],
                "historical_cases": configured_indexes["historical_case_index"],
                "case_evidence": configured_indexes["case_evidence_index"],
            },
        )

    def _default_historical_retriever(self) -> LocalHistoricalCaseRetriever | AzureHistoricalCaseRetriever:
        azure = AzureHistoricalCaseRetriever()
        if self.config.use_azure_search and azure.is_configured:
            return azure
        return LocalHistoricalCaseRetriever()

    def _default_evidence_retriever(self) -> LocalCaseEvidenceRetriever | AzureCaseEvidenceRetriever:
        azure = AzureCaseEvidenceRetriever()
        if self.config.use_azure_search and azure.is_configured:
            return azure
        return LocalCaseEvidenceRetriever()

    def _combined_mode(self) -> str:
        modes = {self.policy_retriever.retrieval_mode, self.historical_retriever.retrieval_mode, self.evidence_retriever.retrieval_mode}
        return modes.pop() if len(modes) == 1 else "mixed"

    def _record_retrieval(self, query: str, index_type: str, results: list, case_id: str | None = None) -> None:
        self.audit_service.create_rag_retrieval_event(
            case_id=case_id,
            event_type=AuditEventType.RAG_RETRIEVAL_COMPLETED,
            rag_query=query,
            rag_sources=[result.source_file for result in results],
            metadata={
                "index_type": index_type,
                "result_count": len(results),
                "retrieval_mode": self._combined_mode(),
            },
        )
