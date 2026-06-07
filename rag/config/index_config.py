from rag.config.rag_config import rag_config


def index_names() -> dict[str, str]:
    return {
        "policy_index": rag_config.policy_index,
        "historical_case_index": rag_config.historical_case_index,
        "case_evidence_index": rag_config.evidence_index,
    }
