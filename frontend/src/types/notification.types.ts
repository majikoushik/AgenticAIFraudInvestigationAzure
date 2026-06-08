export type NotificationPriority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
export type NotificationChannel = "IN_APP" | "LOCAL" | "EMAIL" | "TEAMS" | "WEBHOOK";
export type NotificationStatus = "PENDING" | "SENT" | "FAILED" | "SKIPPED" | "READ" | "ARCHIVED";
export type NotificationEventType = string;

export type NotificationDeliveryRecord = {
  channel: NotificationChannel;
  status: NotificationStatus;
  attempt_count: number;
  last_attempt_at: string | null;
  error_message: string | null;
  sent_at: string | null;
};

export type NotificationResponse = {
  notification_id: string;
  event_type: NotificationEventType;
  priority: NotificationPriority;
  title: string;
  message: string;
  recipient_type: string;
  recipient_id: string | null;
  recipient_role: string | null;
  recipient_team: string | null;
  channels: NotificationChannel[];
  status: NotificationStatus;
  read: boolean;
  archived: boolean;
  case_id: string | null;
  alert_id: string | null;
  incident_id: string | null;
  metadata: Record<string, unknown>;
  delivery_records: NotificationDeliveryRecord[];
  created_at: string;
  sent_at: string | null;
  read_at: string | null;
  archived_at: string | null;
};

export type NotificationListResponse = {
  count: number;
  notifications: NotificationResponse[];
};

export type NotificationSummary = {
  user_id: string;
  unread_count: number;
  critical_unread_count: number;
  high_unread_count: number;
  total_count: number;
  latest_notification_at: string | null;
};

export type NotificationPreference = {
  user_id: string;
  role: string | null;
  team: string | null;
  enabled: boolean;
  channels: NotificationChannel[];
  event_preferences: Record<string, unknown>;
  quiet_hours: { enabled: boolean; start: string; end: string; timezone: string };
  updated_at: string | null;
};
