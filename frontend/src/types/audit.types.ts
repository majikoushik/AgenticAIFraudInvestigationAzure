export type AuditEvent = {
  audit_id: string;
  case_id: string;
  event_type: string;
  actor: string;
  actor_role: string;
  previous_status: string | null;
  new_status: string | null;
  decision: string | null;
  reason_code: string | null;
  comment: string | null;
  ai_recommendation: string | null;
  human_decision: string | null;
  human_override: boolean;
  override_reason: string | null;
  timestamp: string;
};

export type AuditTrail = {
  case_id: string;
  events: AuditEvent[];
};
