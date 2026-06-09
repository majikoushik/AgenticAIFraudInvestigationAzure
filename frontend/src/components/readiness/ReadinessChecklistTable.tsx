"use client";

import { useState } from "react";
import type { ReadinessCategoryResult, ReadinessCheckResult } from "@/types/readiness.types";
import { ReadinessCheckStatusBadge } from "./ReadinessCheckStatusBadge";
import { ReadinessSeverityBadge } from "./ReadinessSeverityBadge";

interface Props {
  categoryResults: ReadinessCategoryResult[];
}

export function ReadinessChecklistTable({ categoryResults }: Props) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const allChecks: (ReadinessCheckResult & { category: string })[] = categoryResults.flatMap((cat) =>
    cat.checks.map((c) => ({ ...c, category: cat.category }))
  );

  const filtered = allChecks.filter((c) => {
    const matchSearch =
      !search ||
      c.check_id.toLowerCase().includes(search.toLowerCase()) ||
      c.title.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "ALL" || c.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="readiness-checklist">
      <div className="readiness-checklist__controls">
        <input
          id="readiness-search"
          type="text"
          placeholder="Search checks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="readiness-checklist__search"
        />
        <select
          id="readiness-status-filter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="readiness-checklist__filter"
        >
          <option value="ALL">All Statuses</option>
          <option value="PASS">Pass</option>
          <option value="FAIL">Fail</option>
          <option value="WARNING">Warning</option>
          <option value="MANUAL_REVIEW_REQUIRED">Manual Review</option>
          <option value="NOT_CHECKED">Not Checked</option>
        </select>
        <span className="readiness-checklist__count">{filtered.length} checks</span>
      </div>

      <div className="readiness-checklist__table-wrapper">
        <table className="readiness-checklist__table">
          <thead>
            <tr>
              <th>Check ID</th>
              <th>Category</th>
              <th>Title</th>
              <th>Status</th>
              <th>Severity</th>
              <th>Score</th>
              <th>Message</th>
              <th>Remediation</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((check) => (
              <tr
                key={check.check_id}
                className={`readiness-row readiness-row--${check.status.toLowerCase()}`}
              >
                <td>
                  <code className="check-id">{check.check_id}</code>
                </td>
                <td>
                  <span className="category-label">{check.category.replace(/_/g, " ")}</span>
                </td>
                <td>{check.title}</td>
                <td>
                  <ReadinessCheckStatusBadge status={check.status} size="sm" />
                </td>
                <td>
                  <ReadinessSeverityBadge severity={check.severity} />
                </td>
                <td>
                  <span className="score-value">{check.score.toFixed(0)}</span>
                </td>
                <td className="readiness-message">{check.message}</td>
                <td className="readiness-remediation">{check.remediation}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={8} className="readiness-empty-row">
                  No checks match your filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
