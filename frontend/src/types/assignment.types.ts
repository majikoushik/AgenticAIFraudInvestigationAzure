export type AssignmentStatus = "UNASSIGNED" | "ASSIGNED" | "ACCEPTED" | "RELEASED" | "TRANSFERRED";
export type AssignmentPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type SlaStatus = "ON_TRACK" | "AT_RISK" | "BREACHED" | "NOT_APPLICABLE";

export type CaseAssignment = {
  assigned_to: string | null;
  assigned_to_name: string | null;
  assigned_to_role: string | null;
  assigned_team: string | null;
  assigned_by: string | null;
  assigned_at: string | null;
  assignment_status: AssignmentStatus;
  assignment_priority: AssignmentPriority;
  sla_due_at: string | null;
  sla_status: SlaStatus;
  last_assignment_action: string | null;
};

export type QueueCase = {
  case_id: string;
  alert_id: string;
  alert_type: string;
  risk_level: string;
  case_status: string;
  assignment_status: AssignmentStatus;
  assigned_to: string | null;
  assigned_to_name: string | null;
  assigned_team: string | null;
  assignment_priority: AssignmentPriority;
  sla_status: SlaStatus;
  sla_due_at: string | null;
  created_at: string;
  reason: string;
};

export type QueueFilters = {
  status?: string;
  priority?: string;
  sla_status?: string;
  risk_level?: string;
  assigned_team?: string;
  sort_by?: string;
  sort_order?: string;
};

export type QueueResponse = {
  queue_name: string;
  count: number;
  cases: QueueCase[];
  filters: Record<string, unknown>;
};

export type AssignmentHistoryRecord = {
  history_id: string;
  case_id: string;
  action: string;
  previous_assigned_to: string | null;
  new_assigned_to: string | null;
  actor: string;
  actor_role: string;
  comment: string | null;
  timestamp: string;
};

export type AssignmentHistoryResponse = {
  case_id: string;
  count: number;
  history: AssignmentHistoryRecord[];
};

export type AssignmentResponse = {
  case_id: string;
  message: string;
  assignment: CaseAssignment;
  case: Record<string, unknown>;
};

export type InvestigatorWorkload = {
  user_id: string;
  display_name: string;
  role: string;
  team: string;
  active_case_count: number;
  accepted_case_count: number;
  cases_by_priority: Record<string, number>;
  workload_status: string;
};

export type WorkloadSummary = {
  total_assigned_cases: number;
  total_unassigned_cases: number;
  active_cases_by_investigator: Record<string, number>;
  cases_by_priority: Record<string, number>;
  cases_by_sla_status: Record<string, number>;
  overloaded_investigators: InvestigatorWorkload[];
  available_investigators: InvestigatorWorkload[];
  average_cases_per_investigator: number;
};
