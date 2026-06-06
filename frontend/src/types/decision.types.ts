export type DecisionValue = "approve" | "hold" | "escalate" | "reject";

export type DecisionRequest = {
  decision: DecisionValue;
  comment: string;
  reviewed_by: string;
};

export type DecisionResponse = {
  case_id: string;
  decision: DecisionValue;
  status: string;
  message: string;
  requires_human_review: boolean;
};
