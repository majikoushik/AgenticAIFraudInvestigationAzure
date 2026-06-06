export type ReviewerRole = "FRAUD_ANALYST" | "FRAUD_MANAGER" | "COMPLIANCE_OFFICER" | "AUDITOR";
export type HumanReviewDecision = "APPROVE" | "HOLD" | "ESCALATE" | "REJECT";
export type OverrideComparisonStatus = "MATCHED" | "OVERRIDDEN" | "AI_RECOMMENDATION_MISSING" | "NOT_APPLICABLE";
export type ReasonCode =
  | "CUSTOMER_CONFIRMED"
  | "SUSPICIOUS_DEVICE"
  | "NEW_BENEFICIARY_RISK"
  | "HIGH_VALUE_TRANSFER"
  | "POLICY_THRESHOLD_BREACH"
  | "INSUFFICIENT_EVIDENCE"
  | "FALSE_POSITIVE"
  | "ESCALATE_TO_AML";

export type HumanReviewRequest = {
  decision: HumanReviewDecision;
  comment: string;
  reviewed_by: string;
  reviewer_role: ReviewerRole;
  reason_code: ReasonCode;
  evidence_acknowledged: boolean;
  policy_acknowledged: boolean;
  override_reason?: string;
};

export type HumanReviewResponse = {
  case_id: string;
  previous_status: string;
  new_status: string;
  decision: HumanReviewDecision;
  reviewed_by: string;
  reviewer_role: ReviewerRole;
  reason_code: ReasonCode;
  ai_recommendation: HumanReviewDecision | null;
  human_decision: HumanReviewDecision;
  human_override: boolean;
  override_reason: string | null;
  override_comparison_status: OverrideComparisonStatus;
  override_detected_at: string | null;
  override_detected_by: string | null;
  message: string;
};

export type OverrideSummary = {
  case_id?: string;
  has_override: boolean;
  ai_recommendation: HumanReviewDecision | null;
  human_decision: HumanReviewDecision | null;
  override_reason: string | null;
  override_detected_at: string | null;
  override_detected_by: string | null;
  override_comparison_status: OverrideComparisonStatus;
};

export type ReviewOptions = {
  reviewer_role: ReviewerRole;
  allowed_decisions: HumanReviewDecision[];
  reason_codes: ReasonCode[];
};
