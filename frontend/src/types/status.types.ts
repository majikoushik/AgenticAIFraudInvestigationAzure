export type CaseStatusInfo = {
  case_id: string;
  status: string;
  allowed_next_statuses: string[];
  status_updated_at: string | null;
  status_updated_by: string | null;
  status_comment: string | null;
};
