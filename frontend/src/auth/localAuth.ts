import type { AppRole } from "@/auth/authConfig";

export type LocalAuthUser = {
  user_id: string;
  display_name: string;
  email: string;
  role: AppRole;
};

const storageKey = "fraud_demo_user";

export const demoUsers: LocalAuthUser[] = [
  { user_id: "fraud_analyst_01", display_name: "Local Fraud Analyst", email: "fraud_analyst_01@example.com", role: "FRAUD_ANALYST" },
  { user_id: "fraud_manager_01", display_name: "Local Fraud Manager", email: "fraud_manager_01@example.com", role: "FRAUD_MANAGER" },
  { user_id: "compliance_officer_01", display_name: "Local Compliance Officer", email: "compliance_officer_01@example.com", role: "COMPLIANCE_OFFICER" },
  { user_id: "auditor_01", display_name: "Local Auditor", email: "auditor_01@example.com", role: "AUDITOR" },
  { user_id: "admin_01", display_name: "Local Admin", email: "admin_01@example.com", role: "ADMIN" }
];

export function getStoredLocalUser(): LocalAuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(storageKey);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as LocalAuthUser;
  } catch {
    return null;
  }
}

export function storeLocalUser(user: LocalAuthUser): void {
  window.localStorage.setItem(storageKey, JSON.stringify(user));
}

export function clearLocalUser(): void {
  window.localStorage.removeItem(storageKey);
}
