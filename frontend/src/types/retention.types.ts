export type DataCategory =
  | "FRAUD_CASE"
  | "AUDIT_EVENT"
  | "HUMAN_REVIEW"
  | "AI_INVESTIGATION_OUTPUT"
  | "AGENT_TRACE"
  | "RAG_RETRIEVAL_RECORD"
  | "POLICY_DOCUMENT"
  | "HISTORICAL_CASE_DOCUMENT"
  | "FEEDBACK_RECORD"
  | "NOTIFICATION_RECORD"
  | "INCIDENT_RECORD"
  | "ALERT_RECORD"
  | "COST_RECORD"
  | "TELEMETRY_RECORD"
  | "CONFIG_HISTORY"
  | "ASSIGNMENT_HISTORY"
  | "EXPORT_FILE";

export type RetentionPolicy = {
  policy_id: string;
  data_category: DataCategory;
  classification: string;
  retention_days: number;
  archive_after_days: number;
  purge_after_days: number;
  auto_archive: boolean;
  auto_purge: boolean;
  requires_approval_for_archive: boolean;
  requires_approval_for_purge: boolean;
  allow_purge: boolean;
  enabled: boolean;
  warnings?: string[];
};

export type RetentionCandidate = {
  record_id: string;
  data_category: DataCategory;
  classification: string;
  retention_status: string;
  recommended_action: string;
  reason: string;
  legal_hold_status: string;
  days_until_purge?: number;
  source_file: string;
  case_id?: string;
};

export type RetentionScanResult = {
  scan_id: string;
  dry_run: boolean;
  records_scanned: number;
  archive_candidates: number;
  purge_candidates: number;
  legal_hold_records: number;
  review_required: number;
  candidates: RetentionCandidate[];
};
