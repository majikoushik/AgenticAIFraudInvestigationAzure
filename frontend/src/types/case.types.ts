export type RiskLevel = "low" | "medium" | "high" | "critical";

export type RiskIndicator = {
  code: string;
  description: string;
  severity: RiskLevel | string;
};

export type CaseSummary = {
  case_id: string;
  alert_id: string;
  customer_id: string;
  severity: RiskLevel | string;
  status: string;
  reason: string;
  created_at: string;
};

export type CustomerProfile = {
  customer_id: string;
  display_name: string;
  account_number_masked: string;
  segment: string;
  risk_tier: string;
  home_country: string;
  account_opened_date: string;
  average_transaction_amount: number;
};

export type Transaction = {
  transaction_id: string;
  customer_id: string;
  amount: number;
  currency: string;
  merchant: string;
  merchant_country: string;
  timestamp: string;
  channel: string;
  payment_method: string;
  beneficiary_id: string | null;
  device_id: string | null;
};

export type Beneficiary = {
  beneficiary_id: string;
  customer_id: string;
  display_name: string;
  relationship_type: string;
  bank_country: string;
  first_seen: string;
  risk_note: string;
};

export type Device = {
  device_id: string;
  customer_id: string;
  device_type: string;
  trusted: boolean;
  last_seen_ip: string;
  last_seen_country: string;
  first_seen: string;
};

export type HistoricalCaseSummary = {
  case_id: string;
  outcome: string;
  summary: string;
};

export type CaseDetail = {
  metadata: {
    case_id: string;
    alert_id: string;
    severity: RiskLevel | string;
    reason: string;
    created_at: string;
  };
  customer: CustomerProfile;
  suspicious_transaction: Transaction;
  beneficiary: Beneficiary | null;
  device: Device | null;
  initial_risk_indicators: RiskIndicator[];
  historical_cases: HistoricalCaseSummary[];
  current_status: string;
};

export type CaseListRow = {
  case_id: string;
  customer_label: string;
  transaction_amount: string;
  alert_type: string;
  risk_level: RiskLevel | string;
  status: string;
  created_at: string;
};
