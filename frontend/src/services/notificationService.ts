import { apiClient } from "@/services/apiClient";
import type { NotificationListResponse, NotificationPreference, NotificationResponse, NotificationSummary } from "@/types/notification.types";

type Filters = { unread_only?: boolean; event_type?: string; priority?: string; archived?: boolean; limit?: number };

function query(filters?: Filters): string {
  const params = new URLSearchParams();
  Object.entries(filters ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") params.set(key, String(value));
  });
  const text = params.toString();
  return text ? `?${text}` : "";
}

export function getMyNotifications(filters?: Filters): Promise<NotificationListResponse> {
  return apiClient<NotificationListResponse>(`/api/v1/notifications/me${query(filters)}`);
}

export function getNotificationSummary(): Promise<NotificationSummary> {
  return apiClient<NotificationSummary>("/api/v1/notifications/summary");
}

export function getNotification(notificationId: string): Promise<NotificationResponse> {
  return apiClient<NotificationResponse>(`/api/v1/notifications/${notificationId}`);
}

export function markAsRead(notificationId: string): Promise<NotificationResponse> {
  return apiClient<NotificationResponse>(`/api/v1/notifications/${notificationId}/read`, { method: "POST" });
}

export function markAllAsRead(): Promise<{ updated_count: number }> {
  return apiClient<{ updated_count: number }>("/api/v1/notifications/read-all", { method: "POST" });
}

export function archiveNotification(notificationId: string): Promise<NotificationResponse> {
  return apiClient<NotificationResponse>(`/api/v1/notifications/${notificationId}/archive`, { method: "POST" });
}

export function getMyPreferences(): Promise<NotificationPreference> {
  return apiClient<NotificationPreference>("/api/v1/notifications/preferences/me");
}

export function updateMyPreferences(payload: Partial<NotificationPreference>): Promise<NotificationPreference> {
  return apiClient<NotificationPreference>("/api/v1/notifications/preferences/me", { method: "PATCH", body: JSON.stringify(payload) });
}

export function sendTestNotification(payload: Record<string, unknown>): Promise<NotificationResponse> {
  return apiClient<NotificationResponse>("/api/v1/notifications/test", { method: "POST", body: JSON.stringify(payload) });
}

export function getAdminNotificationHealth(): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>("/api/v1/admin/notifications/health");
}
