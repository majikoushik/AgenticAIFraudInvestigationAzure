import { apiClient } from "@/services/apiClient";
import type { FeedbackAnalyticsResponse, FeedbackBacklogListResponse, FeedbackCreateRequest, FeedbackListResponse, FeedbackRecord } from "@/types/feedback.types";

export function submitFeedback(payload: FeedbackCreateRequest): Promise<FeedbackRecord> {
  return apiClient<FeedbackRecord>("/api/v1/feedback", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getFeedback(params: Record<string, string | undefined> = {}): Promise<FeedbackListResponse> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  const suffix = query.toString() ? `?${query}` : "";
  return apiClient<FeedbackListResponse>(`/api/v1/feedback${suffix}`);
}

export function getCaseFeedback(caseId: string): Promise<FeedbackListResponse> {
  return apiClient<FeedbackListResponse>(`/api/v1/cases/${caseId}/feedback`);
}

export function updateFeedbackDisposition(feedbackId: string, disposition: string, comment?: string): Promise<FeedbackRecord> {
  return apiClient<FeedbackRecord>(`/api/v1/feedback/${feedbackId}/disposition`, {
    method: "PATCH",
    body: JSON.stringify({ disposition, comment })
  });
}

export function getFeedbackAnalytics(): Promise<FeedbackAnalyticsResponse> {
  return apiClient<FeedbackAnalyticsResponse>("/api/v1/feedback/analytics/summary");
}

export function getFeedbackBacklog(): Promise<FeedbackBacklogListResponse> {
  return apiClient<FeedbackBacklogListResponse>("/api/v1/feedback/backlog");
}

export function updateBacklogStatus(backlogId: string, status: string): Promise<unknown> {
  return apiClient(`/api/v1/feedback/backlog/${backlogId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status })
  });
}

export function exportFeedbackEvalDataset(): Promise<{ exported_count: number; target_path: string }> {
  return apiClient<{ exported_count: number; target_path: string }>("/api/v1/feedback/export/eval-dataset", { method: "POST" });
}
