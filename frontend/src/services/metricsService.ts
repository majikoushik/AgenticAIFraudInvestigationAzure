import { apiClient } from "@/services/apiClient";
import type {
  AiVsHumanMetrics,
  AuditMetrics,
  CaseStatusMetrics,
  MetricsSummary,
  OperationsMetrics
} from "@/types/metrics.types";

export function getMetricsSummary(): Promise<MetricsSummary> {
  return apiClient<MetricsSummary>("/api/v1/metrics/summary");
}

export function getCaseStatusMetrics(): Promise<CaseStatusMetrics> {
  return apiClient<CaseStatusMetrics>("/api/v1/metrics/case-status");
}

export function getAiVsHumanMetrics(): Promise<AiVsHumanMetrics> {
  return apiClient<AiVsHumanMetrics>("/api/v1/metrics/ai-vs-human");
}

export function getOperationsMetrics(): Promise<OperationsMetrics> {
  return apiClient<OperationsMetrics>("/api/v1/metrics/operations");
}

export function getAuditMetrics(): Promise<AuditMetrics> {
  return apiClient<AuditMetrics>("/api/v1/metrics/audit");
}

export function getTimeseriesMetrics(): Promise<Record<string, Record<string, number>>> {
  return apiClient<Record<string, Record<string, number>>>("/api/v1/metrics/timeseries");
}
