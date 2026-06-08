export type FeedbackTargetType =
  | "INVESTIGATION_SUMMARY"
  | "AI_RECOMMENDATION"
  | "POLICY_CITATION"
  | "SIMILAR_CASE_RETRIEVAL"
  | "RISK_INDICATOR"
  | "REVIEWER_VALIDATION"
  | "AGENT_TRACE"
  | "OVERALL_AI_OUTPUT";

export type FeedbackRating = "VERY_POOR" | "POOR" | "ACCEPTABLE" | "GOOD" | "EXCELLENT";
export type FeedbackSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type FeedbackDisposition = "NEW" | "TRIAGED" | "ACCEPTED_FOR_IMPROVEMENT" | "REJECTED_NO_ACTION" | "CONVERTED_TO_EVAL_CASE" | "PROMPT_BACKLOG_CREATED" | "RAG_BACKLOG_CREATED" | "RESOLVED" | "CLOSED";

export type FeedbackIssueType =
  | "INCORRECT_RECOMMENDATION"
  | "MISSING_EVIDENCE"
  | "UNSUPPORTED_CLAIM"
  | "WRONG_POLICY_CITATION"
  | "MISSING_POLICY_CITATION"
  | "IRRELEVANT_SIMILAR_CASE"
  | "MISSING_SIMILAR_CASE"
  | "POOR_EXPLANATION"
  | "TOO_VERBOSE"
  | "TOO_SHORT"
  | "HALLUCINATION_SUSPECTED"
  | "SAFETY_CONCERN"
  | "PII_CONCERN"
  | "PROMPT_INJECTION_CONCERN"
  | "OTHER";

export type FeedbackCreateRequest = {
  case_id: string;
  target_type: FeedbackTargetType;
  target_id?: string | null;
  rating: FeedbackRating;
  issue_types: FeedbackIssueType[];
  severity: FeedbackSeverity;
  comment?: string | null;
  suggested_correction?: string | null;
  expected_recommendation?: string | null;
  actual_ai_recommendation?: string | null;
  human_decision?: string | null;
  policy_source_file?: string | null;
  policy_chunk_id?: string | null;
  agent_name?: string | null;
  sanitized_ai_output_snapshot?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
};

export type FeedbackRecord = FeedbackCreateRequest & {
  feedback_id: string;
  submitted_by: string;
  submitted_by_role: string;
  disposition: FeedbackDisposition;
  case_status_at_feedback?: string | null;
  ai_provider?: string | null;
  model_or_deployment?: string | null;
  created_at: string;
  updated_at: string;
};

export type FeedbackListResponse = {
  count: number;
  feedback_records: FeedbackRecord[];
};

export type FeedbackBacklogItem = {
  backlog_id: string;
  feedback_id: string;
  backlog_type: string;
  title: string;
  description: string;
  priority: FeedbackSeverity;
  status: string;
  owner: string;
  created_at: string;
  updated_at?: string | null;
  metadata: Record<string, unknown>;
};

export type FeedbackBacklogListResponse = {
  count: number;
  backlog_items: FeedbackBacklogItem[];
};

export type FeedbackAnalyticsResponse = {
  summary: Record<string, number>;
  by_rating: Record<string, number>;
  by_issue_type: Record<string, number>;
  by_target_type: Record<string, number>;
  by_agent: Record<string, number>;
  by_ai_provider: Record<string, number>;
  recommendation_quality: Record<string, unknown>;
  rag_quality: Record<string, unknown>;
  trends: Record<string, Record<string, number>>;
  backlog: Record<string, number>;
};
