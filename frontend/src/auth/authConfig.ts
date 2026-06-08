export type AppRole = "FRAUD_ANALYST" | "FRAUD_MANAGER" | "COMPLIANCE_OFFICER" | "AUDITOR" | "ADMIN";

export const authMode = process.env.NEXT_PUBLIC_AUTH_MODE ?? "local";

export const entraConfig = {
  clientId: process.env.NEXT_PUBLIC_ENTRA_CLIENT_ID ?? "",
  tenantId: process.env.NEXT_PUBLIC_ENTRA_TENANT_ID ?? "",
  authority: process.env.NEXT_PUBLIC_ENTRA_AUTHORITY ?? "",
  redirectUri: process.env.NEXT_PUBLIC_ENTRA_REDIRECT_URI ?? "http://localhost:3000",
  apiScope: process.env.NEXT_PUBLIC_API_SCOPE ?? ""
};

const assignmentRead = ["VIEW_OWN_QUEUE", "VIEW_ASSIGNMENT_HISTORY"];
const assignmentManage = ["VIEW_TEAM_QUEUE", "VIEW_UNASSIGNED_QUEUE", "ASSIGN_CASE", "REASSIGN_CASE", "RELEASE_CASE", "ACCEPT_CASE", "TRANSFER_CASE"];
const notifications = ["VIEW_NOTIFICATIONS"];
const feedbackSubmit = ["SUBMIT_AI_FEEDBACK"];
const feedbackManage = ["VIEW_AI_FEEDBACK", "MANAGE_AI_FEEDBACK"];

export const rolePermissions: Record<AppRole, string[]> = {
  FRAUD_ANALYST: ["VIEW_CASES", "VIEW_CASE_DETAILS", "RUN_AI_INVESTIGATION", "SUBMIT_HUMAN_REVIEW", "HOLD_DECISION", "ESCALATE_DECISION", "REJECT_DECISION", "VIEW_AUDIT", "VIEW_METRICS", ...assignmentRead, "ACCEPT_CASE", "RELEASE_CASE", ...notifications, ...feedbackSubmit],
  FRAUD_MANAGER: ["VIEW_CASES", "VIEW_CASE_DETAILS", "RUN_AI_INVESTIGATION", "SUBMIT_HUMAN_REVIEW", "APPROVE_DECISION", "HOLD_DECISION", "ESCALATE_DECISION", "REJECT_DECISION", "CLOSE_CASE", "VIEW_AUDIT", "VIEW_METRICS", ...assignmentRead, ...assignmentManage, ...notifications, ...feedbackSubmit, ...feedbackManage],
  COMPLIANCE_OFFICER: ["VIEW_CASES", "VIEW_CASE_DETAILS", "RUN_AI_INVESTIGATION", "SUBMIT_HUMAN_REVIEW", "HOLD_DECISION", "ESCALATE_DECISION", "CLOSE_CASE", "VIEW_AUDIT", "VIEW_METRICS", ...assignmentRead, "VIEW_TEAM_QUEUE", "ACCEPT_CASE", "RELEASE_CASE", ...notifications, ...feedbackSubmit, ...feedbackManage],
  AUDITOR: ["VIEW_CASES", "VIEW_CASE_DETAILS", "VIEW_AUDIT", "VIEW_METRICS", "VIEW_TEAM_QUEUE", "VIEW_ASSIGNMENT_HISTORY", ...notifications, "VIEW_AI_FEEDBACK"],
  ADMIN: ["VIEW_CASES", "VIEW_CASE_DETAILS", "RUN_AI_INVESTIGATION", "SUBMIT_HUMAN_REVIEW", "APPROVE_DECISION", "HOLD_DECISION", "ESCALATE_DECISION", "REJECT_DECISION", "CLOSE_CASE", "VIEW_AUDIT", "VIEW_METRICS", "ADMIN_CONFIG", ...assignmentRead, ...assignmentManage, ...notifications, "MANAGE_NOTIFICATIONS", ...feedbackSubmit, ...feedbackManage, "EXPORT_AI_FEEDBACK"]
};

export const decisionOptionsByRole: Record<AppRole, string[]> = {
  FRAUD_ANALYST: ["HOLD", "ESCALATE", "REJECT"],
  FRAUD_MANAGER: ["APPROVE", "HOLD", "ESCALATE", "REJECT"],
  COMPLIANCE_OFFICER: ["HOLD", "ESCALATE"],
  AUDITOR: [],
  ADMIN: ["APPROVE", "HOLD", "ESCALATE", "REJECT"]
};
