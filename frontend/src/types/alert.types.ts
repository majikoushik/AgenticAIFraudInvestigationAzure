export type AlertEvent = {
  alert_id: string;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  source: string;
  status: string;
  metric_name?: string;
  metric_value?: number;
  threshold_value?: number;
  recommended_runbook?: string;
  created_at: string;
  resolved_at?: string | null;
};

export type AlertListResponse = {
  count: number;
  alerts: AlertEvent[];
};
