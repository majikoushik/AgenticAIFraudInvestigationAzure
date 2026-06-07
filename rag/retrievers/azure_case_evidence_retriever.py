from rag.config.rag_config import rag_config
from rag.retrievers.azure_search_base import AzureSearchRetrieverBase


class AzureCaseEvidenceRetriever(AzureSearchRetrieverBase):
    def __init__(self) -> None:
        super().__init__(rag_config.evidence_index)
