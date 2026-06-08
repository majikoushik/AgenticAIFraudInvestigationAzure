from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import FeedbackDisposition, FeedbackIssueType, FeedbackRating, FeedbackSeverity, FeedbackTargetType


class FeedbackCreateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    case_id: str
    target_type: FeedbackTargetType
    target_id: str | None = None
    rating: FeedbackRating
    issue_types: list[FeedbackIssueType] = Field(default_factory=list)
    severity: FeedbackSeverity = FeedbackSeverity.MEDIUM
    comment: str | None = None
    suggested_correction: str | None = None
    expected_recommendation: str | None = None
    actual_ai_recommendation: str | None = None
    human_decision: str | None = None
    policy_source_file: str | None = None
    policy_chunk_id: str | None = None
    agent_name: str | None = None
    sanitized_ai_output_snapshot: dict[str, Any] = Field(default_factory=dict)
    ai_provider: str | None = None
    model_or_deployment: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    feedback_id: str
    case_id: str
    target_type: FeedbackTargetType
    target_id: str | None = None
    rating: FeedbackRating
    issue_types: list[FeedbackIssueType] = Field(default_factory=list)
    severity: FeedbackSeverity
    comment: str | None = None
    suggested_correction: str | None = None
    actual_ai_recommendation: str | None = None
    expected_recommendation: str | None = None
    human_decision: str | None = None
    submitted_by: str
    submitted_by_role: str
    disposition: FeedbackDisposition
    case_status_at_feedback: str | None = None
    ai_provider: str | None = None
    model_or_deployment: str | None = None
    agent_name: str | None = None
    policy_source_file: str | None = None
    policy_chunk_id: str | None = None
    sanitized_ai_output_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackListResponse(BaseModel):
    count: int
    feedback_records: list[FeedbackResponse]


class FeedbackDispositionUpdateRequest(BaseModel):
    disposition: FeedbackDisposition
    updated_by: str | None = None
    comment: str | None = None


class FeedbackBacklogItem(BaseModel):
    backlog_id: str
    feedback_id: str
    backlog_type: Literal["PROMPT_IMPROVEMENT", "RAG_IMPROVEMENT", "EVALUATION_CASE", "SAFETY_REVIEW", "MODEL_ROUTING_REVIEW", "DATA_QUALITY_REVIEW"]
    title: str
    description: str
    priority: FeedbackSeverity
    status: str = "OPEN"
    owner: str = "AI Quality Team"
    created_at: str
    updated_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackBacklogListResponse(BaseModel):
    count: int
    backlog_items: list[FeedbackBacklogItem]


class FeedbackBacklogStatusUpdateRequest(BaseModel):
    status: str
    updated_by: str | None = None
    comment: str | None = None


class FeedbackAnalyticsResponse(BaseModel):
    summary: dict[str, Any]
    by_rating: dict[str, int]
    by_issue_type: dict[str, int]
    by_target_type: dict[str, int]
    by_agent: dict[str, int]
    by_ai_provider: dict[str, int]
    recommendation_quality: dict[str, Any]
    rag_quality: dict[str, Any]
    trends: dict[str, Any]
    backlog: dict[str, Any]


class FeedbackExportResponse(BaseModel):
    exported_count: int
    target_path: str
    eval_cases: list[dict[str, Any]]
