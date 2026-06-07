from pydantic import BaseModel


class CaseStatusMetrics(BaseModel):
    total_cases: int
    new_cases: int
    ai_investigation_in_progress_cases: int
    ai_investigation_completed_cases: int
    pending_human_review_cases: int
    approved_cases: int
    held_cases: int
    escalated_cases: int
    rejected_cases: int
    closed_cases: int
    status_counts: dict[str, int]
    status_percentages: dict[str, float]


class AIRecommendationMetrics(BaseModel):
    total_ai_recommendations: int
    recommendation_counts: dict[str, int]
    recommendation_percentages: dict[str, float]
    cases_missing_ai_recommendation: int


class HumanDecisionMetrics(BaseModel):
    total_human_decisions: int
    decision_counts: dict[str, int]
    decision_percentages: dict[str, float]
    cases_without_human_decision: int


class HumanOverrideMetrics(BaseModel):
    total_reviewed_cases: int
    total_overrides: int
    override_rate_percentage: float
    ai_human_match_count: int
    ai_human_match_rate_percentage: float
    override_counts_by_ai_recommendation: dict[str, int]
    override_counts_by_human_decision: dict[str, int]
    override_pairs: list[dict]


class InvestigationTimeMetrics(BaseModel):
    average_ai_investigation_duration_seconds: float
    minimum_ai_investigation_duration_seconds: float
    maximum_ai_investigation_duration_seconds: float
    cases_with_missing_investigation_duration: int


class HumanReviewTimeMetrics(BaseModel):
    average_human_review_wait_time_seconds: float
    minimum_human_review_wait_time_seconds: float
    maximum_human_review_wait_time_seconds: float
    cases_with_missing_review_duration: int


class AgentExecutionMetrics(BaseModel):
    total_agent_executions: int
    agent_success_count: int
    agent_failure_count: int
    agent_failure_rate_percentage: float
    execution_count_by_agent: dict[str, int]
    failure_count_by_agent: dict[str, int]
    average_duration_by_agent: dict[str, float]


class RagRetrievalMetrics(BaseModel):
    total_rag_retrievals: int
    rag_success_count: int
    rag_failure_count: int
    rag_failure_rate_percentage: float
    retrieval_count_by_mode: dict[str, int]
    average_result_count: float
    top_retrieved_sources: list[dict]


class PolicyCitationMetrics(BaseModel):
    cases_with_policy_references: int
    cases_without_policy_references: int
    policy_reference_rate_percentage: float
    top_policy_sources: list[dict]


class AuditMetrics(BaseModel):
    total_audit_events: int
    audit_events_by_category: dict[str, int]
    audit_events_by_type: dict[str, int]
    audit_events_by_actor_role: dict[str, int]
    latest_audit_event_timestamp: str | None


class MetricsSummaryResponse(BaseModel):
    case_status_metrics: CaseStatusMetrics
    ai_recommendation_metrics: AIRecommendationMetrics
    human_decision_metrics: HumanDecisionMetrics
    human_override_metrics: HumanOverrideMetrics
    investigation_time_metrics: InvestigationTimeMetrics
    human_review_time_metrics: HumanReviewTimeMetrics
    agent_execution_metrics: AgentExecutionMetrics
    rag_retrieval_metrics: RagRetrievalMetrics
    policy_citation_metrics: PolicyCitationMetrics
    audit_metrics: AuditMetrics


class AiVsHumanMetricsResponse(BaseModel):
    ai_recommendation_metrics: AIRecommendationMetrics
    human_decision_metrics: HumanDecisionMetrics
    human_override_metrics: HumanOverrideMetrics
    override_pairs: list[dict]


class OperationsMetricsResponse(BaseModel):
    investigation_time_metrics: InvestigationTimeMetrics
    human_review_time_metrics: HumanReviewTimeMetrics
    agent_execution_metrics: AgentExecutionMetrics
    rag_retrieval_metrics: RagRetrievalMetrics
