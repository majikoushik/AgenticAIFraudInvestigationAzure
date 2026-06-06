from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState
from rag.retrievers.citation_builder import build_policy_reference
from rag.retrievers.hybrid_retriever import HybridPolicyRetriever


class PolicyRagAgent(BaseAgent):
    name = "PolicyRagAgent"

    def __init__(self, retriever: HybridPolicyRetriever | None = None) -> None:
        self.retriever = retriever or HybridPolicyRetriever()

    def run(self, state: InvestigationState) -> dict:
        query = self._build_query(state)
        matches = self.retriever.search(query, top_k=3)

        return {
            "query": query,
            "retrieval_mode": self.retriever.retrieval_mode,
            "policy_references": [build_policy_reference(match) for match in matches],
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
