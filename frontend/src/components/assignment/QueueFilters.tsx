"use client";

import type { QueueFilters as FilterValues } from "@/types/assignment.types";

type Props = {
  filters: FilterValues;
  onChange: (filters: FilterValues) => void;
};

export function QueueFilters({ filters, onChange }: Props) {
  return (
    <div className="queue-filters">
      <select value={filters.priority ?? ""} onChange={(event) => onChange({ ...filters, priority: event.target.value || undefined })}>
        <option value="">All priorities</option>
        <option value="CRITICAL">Critical</option>
        <option value="HIGH">High</option>
        <option value="MEDIUM">Medium</option>
        <option value="LOW">Low</option>
      </select>
      <select value={filters.sla_status ?? ""} onChange={(event) => onChange({ ...filters, sla_status: event.target.value || undefined })}>
        <option value="">All SLA</option>
        <option value="BREACHED">Breached</option>
        <option value="AT_RISK">At risk</option>
        <option value="ON_TRACK">On track</option>
      </select>
      <select value={filters.status ?? ""} onChange={(event) => onChange({ ...filters, status: event.target.value || undefined })}>
        <option value="">All assignment states</option>
        <option value="UNASSIGNED">Unassigned</option>
        <option value="ASSIGNED">Assigned</option>
        <option value="ACCEPTED">Accepted</option>
      </select>
    </div>
  );
}
