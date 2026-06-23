"use client";

import { useEffect, useState } from "react";
import { getChecklist } from "@/services/readinessService";
import type { ReadinessCheckDefinition } from "@/types/readiness.types";
import { ReadinessSeverityBadge } from "@/components/readiness/ReadinessSeverityBadge";

export default function ReadinessChecklistPage() {
  const [data, setData] = useState<{
    total: number;
    categories: string[];
    checklist: Record<string, ReadinessCheckDefinition[]>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    getChecklist()
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Failed to load checklist"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="readiness-loading">Loading checklist...</div>;
  if (error) return <div className="readiness-error readiness-error--page">{error}</div>;
  if (!data) return null;

  const filteredCategories = data.categories.filter((cat) => {
    if (!search) return true;
    const checks = data.checklist[cat] ?? [];
    return (
      cat.toLowerCase().includes(search.toLowerCase()) ||
      checks.some(
        (c) =>
          c.check_id.toLowerCase().includes(search.toLowerCase()) ||
          c.title.toLowerCase().includes(search.toLowerCase())
      )
    );
  });

  return (
    <main className="page readiness-page" aria-label="Production Readiness Checklist Definitions">
      <div className="page__header">
        <h1 className="page__title">Readiness Checklist Definitions</h1>
        <p className="page__subtitle">
          {data.total} checks across {data.categories.length} categories
        </p>
      </div>

      <div className="readiness-controls">
        <input
          id="checklist-search"
          type="text"
          className="form-input"
          placeholder="Search checks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {filteredCategories.map((cat) => {
        const checks = (data.checklist[cat] ?? []).filter(
          (c) =>
            !search ||
            c.check_id.toLowerCase().includes(search.toLowerCase()) ||
            c.title.toLowerCase().includes(search.toLowerCase())
        );
        if (!checks.length) return null;
        const isExpanded = expanded === cat;

        return (
          <div key={cat} className="checklist-category">
            <button
              id={`cat-${cat}`}
              className="checklist-category__header"
              onClick={() => setExpanded(isExpanded ? null : cat)}
              aria-expanded={isExpanded}
            >
              <span className="checklist-category__name">{cat.replace(/_/g, " ")}</span>
              <span className="checklist-category__count">{checks.length} checks</span>
              <span className="checklist-category__chevron">{isExpanded ? "▲" : "▼"}</span>
            </button>

            {isExpanded && (
              <div className="checklist-category__body">
                <table className="readiness-table">
                  <thead>
                    <tr>
                      <th>Check ID</th>
                      <th>Title</th>
                      <th>Type</th>
                      <th>Severity</th>
                      <th>Owner</th>
                      <th>Manual Evidence?</th>
                      <th>Remediation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {checks.map((c) => (
                      <tr key={c.check_id}>
                        <td><code>{c.check_id}</code></td>
                        <td title={c.description}>{c.title}</td>
                        <td>
                          <span className={`check-type check-type--${c.check_type.toLowerCase()}`}>
                            {c.check_type}
                          </span>
                        </td>
                        <td><ReadinessSeverityBadge severity={c.severity} /></td>
                        <td>{c.owner}</td>
                        <td>{c.manual_evidence_required ? "✅ Yes" : "—"}</td>
                        <td className="readiness-remediation">{c.remediation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </main>
  );
}
