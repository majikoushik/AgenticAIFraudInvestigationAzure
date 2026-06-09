// Production Readiness Types
// All types mirror the backend Pydantic schemas

export type ReadinessStatus =
  | "PASS"
  | "FAIL"
  | "WARNING"
  | "NOT_APPLICABLE"
  | "MANUAL_REVIEW_REQUIRED"
  | "NOT_CHECKED";

export type ReadinessSeverity = "BLOCKER" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

export type GoLiveDecision =
  | "READY"
  | "READY_WITH_RISKS"
  | "NOT_READY"
  | "MANUAL_REVIEW_REQUIRED";

export type ReadinessCheckType = "AUTOMATED" | "MANUAL" | "HYBRID";

export type ReadinessRiskStatus = "OPEN" | "MITIGATED" | "ACCEPTED" | "CLOSED";

export type ReadinessEvidenceType =
  | "TEXT"
  | "FILE_REFERENCE"
  | "URL"
  | "CHECK_OUTPUT";

// ---------------------------------------------------------------------------
// Check Definition
// ---------------------------------------------------------------------------
export interface ReadinessCheckDefinition {
  check_id: string;
  category: string;
  title: string;
  description: string;
  check_type: ReadinessCheckType;
  severity: ReadinessSeverity;
  automated: boolean;
  manual_evidence_required: boolean;
  recommended_evidence: string;
  remediation: string;
  owner: string;
}

// ---------------------------------------------------------------------------
// Check Result
// ---------------------------------------------------------------------------
export interface ReadinessCheckResult {
  check_id: string;
  category: string;
  title: string;
  status: ReadinessStatus;
  severity: ReadinessSeverity;
  score: number;
  message: string;
  evidence: string[];
  manual_notes: string | null;
  remediation: string;
  checked_at: string;
}

// ---------------------------------------------------------------------------
// Category Result
// ---------------------------------------------------------------------------
export interface ReadinessCategoryResult {
  category: string;
  score: number;
  pass_count: number;
  fail_count: number;
  warning_count: number;
  manual_review_count: number;
  not_checked_count: number;
  not_applicable_count: number;
  blocker_fail_count: number;
  checks: ReadinessCheckResult[];
}

// ---------------------------------------------------------------------------
// Assessment
// ---------------------------------------------------------------------------
export interface ReadinessAssessment {
  assessment_id: string;
  environment: string;
  overall_score: number;
  go_live_decision: GoLiveDecision;
  blocking_issue_count: number;
  high_risk_count: number;
  warning_count: number;
  manual_review_required_count: number;
  total_checks: number;
  category_results: ReadinessCategoryResult[];
  top_risks: string[];
  created_by: string;
  created_at: string;
  completed_at?: string;
  summary: string;
  comment?: string;
  evidence_items?: ReadinessEvidence[];
}

// ---------------------------------------------------------------------------
// Risk Register
// ---------------------------------------------------------------------------
export interface ReadinessRiskItem {
  risk_id: string;
  title: string;
  description: string;
  category: string;
  severity: ReadinessSeverity;
  status: ReadinessRiskStatus;
  owner: string;
  mitigation_plan: string | null;
  target_date: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  assessment_id: string | null;
  check_id: string | null;
  close_comment: string | null;
}

export interface ReadinessRiskCreatePayload {
  title: string;
  description: string;
  category: string;
  severity: ReadinessSeverity;
  owner: string;
  mitigation_plan?: string;
  target_date?: string;
}

export interface ReadinessRiskUpdatePayload {
  title?: string;
  description?: string;
  severity?: ReadinessSeverity;
  status?: ReadinessRiskStatus;
  owner?: string;
  mitigation_plan?: string;
  target_date?: string;
}

// ---------------------------------------------------------------------------
// Evidence
// ---------------------------------------------------------------------------
export interface ReadinessEvidence {
  evidence_id: string;
  check_id: string;
  assessment_id: string;
  evidence_type: ReadinessEvidenceType;
  description: string;
  submitted_by: string;
  submitted_at: string;
  metadata: Record<string, unknown>;
}

export interface ReadinessEvidencePayload {
  check_id: string;
  evidence_type: ReadinessEvidenceType;
  description: string;
  metadata?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Report
// ---------------------------------------------------------------------------
export interface ReadinessReportResult {
  assessment_id: string;
  format: string;
  export_path: string;
  content_preview: string;
  exported_at: string;
}

// ---------------------------------------------------------------------------
// Go-live Decision
// ---------------------------------------------------------------------------
export interface GoLiveDecisionResponse {
  assessment_id: string;
  environment: string;
  go_live_decision: GoLiveDecision;
  overall_score: number;
  blocking_issue_count: number;
  high_risk_count: number;
  warning_count: number;
  manual_review_required_count: number;
  rationale: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// API payloads
// ---------------------------------------------------------------------------
export interface RunAssessmentPayload {
  environment: string;
  categories?: string[] | null;
  create_risks_from_failures: boolean;
  comment?: string;
}
