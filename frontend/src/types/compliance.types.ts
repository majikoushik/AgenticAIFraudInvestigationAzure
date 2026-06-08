export type ComplianceSummary = {
  total_records_by_category: Record<string, number>;
  archive_candidates: number;
  purge_candidates: number;
  review_required_count: number;
  legal_hold_count: number;
  latest_scan_timestamp?: string;
  exports_generated?: number;
  policy_count?: number;
  disabled_policies?: number;
  compliance_warnings?: string[];
};

export type ComplianceExport = {
  export_id: string;
  case_id: string;
  status: string;
  requested_by: string;
  requested_at: string;
  completed_at?: string;
  output_path?: string;
  manifest: Record<string, unknown>;
};
