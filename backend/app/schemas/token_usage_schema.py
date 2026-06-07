from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TokenUsageRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    usage_id: str
    case_id: str | None = None
    correlation_id: str | None = None
    agent_name: str
    operation_name: str
    ai_provider: str
    model_or_deployment: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    input_char_count: int = 0
    output_char_count: int = 0
    rag_context_tokens_estimate: int = 0
    retrieval_source_count: int = 0
    retry_count: int = 0
    fallback_used: bool = False
    success: bool = True
    error_type: str | None = None
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
