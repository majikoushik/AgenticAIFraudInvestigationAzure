export type CaseStatusMetrics = {
  total_cases: number;
  new_cases: number;
  ai_investigation_in_progress_cases: number;
  ai_investigation_completed_cases: number;
  pending_human_review_cases: number;
  approved_cases: number;
  held_cases: number;
  escalated_cases: number;
  rejected_cases: number;
  closed_cases: number;
  status_counts: Record<string, number>;
  status_percentages: Record<string, number>;
};

export type AIRecommendationMetrics = {
  total_ai_recommendations: number;
  recommendation_counts: Record<string, number>;
  recommendation_percentages: Record<string, number>;
  cases_missing_ai_recommendation: number;
};

export type HumanDecisionMetrics = {
  total_human_decisions: number;
  decision_counts: Record<string, number>;
  decision_percentages: Record<string, number>;
  cases_without_human_decision: number;
};

export type HumanOverrideMetrics = {
  total_reviewed_cases: number;
  total_overrides: number;
  override_rate_percentage: number;
  ai_human_match_count: number;
  ai_human_match_rate_percentage: number;
  override_counts_by_ai_recommendation: Record<string, number>;
  override_counts_by_human_decision: Record<string, number>;
  override_pairs: Array<{ ai_recommendation: string; human_decision: string; count: number }>;
};

export type InvestigationTimeMetrics = {
  average_ai_investigation_duration_seconds: number;
  minimum_ai_investigation_duration_seconds: number;
  maximum_ai_investigation_duration_seconds: number;
  cases_with_missing_investigation_duration: number;
};

export type HumanReviewTimeMetrics = {
  average_human_review_wait_time_seconds: number;
  minimum_human_review_wait_time_seconds: number;
  maximum_human_review_wait_time_seconds: number;
  cases_with_missing_review_duration: number;
};

export type AgentExecutionMetrics = {
  total_agent_executions: number;
  agent_success_count: number;
  agent_failure_count: number;
  agent_failure_rate_percentage: number;
  execution_count_by_agent: Record<string, number>;
  failure_count_by_agent: Record<string, number>;
  average_duration_by_agent: Record<string, number>;
};

export type RagRetrievalMetrics = {
  total_rag_retrievals: number;
  rag_success_count: number;
  rag_failure_count: number;
  rag_failure_rate_percentage: number;
  retrieval_count_by_mode: Record<string, number>;
  average_result_count: number;
  top_retrieved_sources: Array<{ name: string; count: number }>;
};

export type PolicyCitationMetrics = {
  cases_with_policy_references: number;
  cases_without_policy_references: number;
  policy_reference_rate_percentage: number;
  top_policy_sources: Array<{ name: string; count: number }>;
};

export type AuditMetrics = {
  total_audit_events: number;
  audit_events_by_category: Record<string, number>;
  audit_events_by_type: Record<string, number>;
  audit_events_by_actor_role: Record<string, number>;
  latest_audit_event_timestamp: string | null;
};

export type MetricsSummary = {
  case_status_metrics: CaseStatusMetrics;
  ai_recommendation_metrics: AIRecommendationMetrics;
  human_decision_metrics: HumanDecisionMetrics;
  human_override_metrics: HumanOverrideMetrics;
  investigation_time_metrics: InvestigationTimeMetrics;
  human_review_time_metrics: HumanReviewTimeMetrics;
  agent_execution_metrics: AgentExecutionMetrics;
  rag_retrieval_metrics: RagRetrievalMetrics;
  policy_citation_metrics: PolicyCitationMetrics;
  audit_metrics: AuditMetrics;
};

export type AiVsHumanMetrics = {
  ai_recommendation_metrics: AIRecommendationMetrics;
  human_decision_metrics: HumanDecisionMetrics;
  human_override_metrics: HumanOverrideMetrics;
  override_pairs: HumanOverrideMetrics["override_pairs"];
};

export type OperationsMetrics = {
  investigation_time_metrics: InvestigationTimeMetrics;
  human_review_time_metrics: HumanReviewTimeMetrics;
  agent_execution_metrics: AgentExecutionMetrics;
  rag_retrieval_metrics: RagRetrievalMetrics;
};
