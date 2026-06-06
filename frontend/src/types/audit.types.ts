export type AuditEventCategory = "CASE" | "AI" | "AGENT" | "RAG" | "HUMAN_REVIEW" | "SECURITY" | "ERROR";
export type AuditEventType = string;

export type AuditEvent = {
  audit_id: string;
  case_id: string | null;
  event_type: AuditEventType;
  event_category: AuditEventCategory;
  actor: string;
  actor_role: string;
  action: string;
  description: string;
  previous_status: string | null;
  new_status: string | null;
  decision: string | null;
  reason_code: string | null;
  ai_recommendation: string | null;
  human_decision: string | null;
  human_override: boolean;
  override_reason: string | null;
  agent_name: string | null;
  tool_name: string | null;
  rag_query: string | null;
  rag_sources: string[];
  error_code: string | null;
  error_message: string | null;
  correlation_id: string | null;
  metadata: Record<string, unknown>;
  timestamp: string;
};

export type AuditEventListResponse = {
  case_id: string | null;
  count: number;
  events: AuditEvent[];
};

export type AuditEventTypeInfo = {
  event_type: string;
  event_category: string;
};

export type AuditSearchFilters = {
  case_id?: string;
  event_type?: string;
  actor?: string;
  actor_role?: string;
  start_date?: string;
  end_date?: string;
};

export type AuditTrail = AuditEventListResponse;
