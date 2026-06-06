export type AuditEntry = {
  case_id: string;
  action: string;
  decision: string | null;
  comment: string | null;
  reviewed_by: string | null;
  created_at: string;
};

export type AuditTrail = {
  case_id: string;
  entries: AuditEntry[];
};
