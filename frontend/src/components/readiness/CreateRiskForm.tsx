"use client";

import { useState } from "react";
import { createRisk } from "@/services/readinessService";
import type { ReadinessSeverity } from "@/types/readiness.types";

interface Props {
  onCreated?: () => void;
}

const SEVERITIES: ReadinessSeverity[] = ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"];
const CATEGORIES = [
  "ARCHITECTURE", "SECURITY", "IDENTITY_AND_ACCESS", "SECRETS_AND_KEY_MANAGEMENT",
  "NETWORKING", "AI_SAFETY_AND_GUARDRAILS", "RAG_AND_KNOWLEDGE_GROUNDING",
  "HUMAN_IN_THE_LOOP", "AUDIT_AND_COMPLIANCE", "DATA_RETENTION", "OBSERVABILITY",
  "ALERTING_AND_INCIDENT_RESPONSE", "RELIABILITY_AND_RESILIENCE", "PERFORMANCE_AND_SCALABILITY",
  "COST_MANAGEMENT", "DEVOPS_AND_RELEASE_MANAGEMENT", "TESTING_AND_QUALITY",
  "OPERATIONS_AND_SUPPORT", "DOCUMENTATION", "BUSINESS_READINESS",
];

export function CreateRiskForm({ onCreated }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("SECURITY");
  const [severity, setSeverity] = useState<ReadinessSeverity>("HIGH");
  const [owner, setOwner] = useState("");
  const [mitigation, setMitigation] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !owner.trim()) return;
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await createRisk({
        title: title.trim(),
        description: description.trim(),
        category,
        severity,
        owner: owner.trim(),
        mitigation_plan: mitigation.trim() || undefined,
        target_date: targetDate || undefined,
      });
      setSuccess(true);
      setTitle(""); setDescription(""); setOwner(""); setMitigation(""); setTargetDate("");
      onCreated?.();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create risk");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="create-risk-form" onSubmit={handleSubmit} aria-label="Create risk form">
      <h4 className="create-risk-form__title">Create Risk Item</h4>

      {error && <div className="readiness-error">{error}</div>}
      {success && <div className="readiness-success">Risk created successfully.</div>}

      <div className="form-row">
        <div className="form-group form-group--grow">
          <label htmlFor="risk-title" className="form-label">Title</label>
          <input id="risk-title" type="text" className="form-input" value={title}
            onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="risk-severity" className="form-label">Severity</label>
          <select id="risk-severity" className="form-select" value={severity}
            onChange={(e) => setSeverity(e.target.value as ReadinessSeverity)}>
            {SEVERITIES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="risk-category" className="form-label">Category</label>
        <select id="risk-category" className="form-select" value={category}
          onChange={(e) => setCategory(e.target.value)}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c.replace(/_/g, " ")}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="risk-description" className="form-label">Description</label>
        <textarea id="risk-description" className="form-textarea" value={description}
          onChange={(e) => setDescription(e.target.value)} rows={3} />
      </div>

      <div className="form-row">
        <div className="form-group form-group--grow">
          <label htmlFor="risk-owner" className="form-label">Owner</label>
          <input id="risk-owner" type="text" className="form-input" value={owner}
            onChange={(e) => setOwner(e.target.value)} required placeholder="Security Team, Platform Team..." />
        </div>
        <div className="form-group">
          <label htmlFor="risk-target-date" className="form-label">Target Date</label>
          <input id="risk-target-date" type="date" className="form-input" value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)} />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="risk-mitigation" className="form-label">Mitigation Plan</label>
        <textarea id="risk-mitigation" className="form-textarea" value={mitigation}
          onChange={(e) => setMitigation(e.target.value)} rows={2} />
      </div>

      <button id="btn-create-risk" type="submit" disabled={loading} className="btn btn--primary">
        {loading ? "Creating..." : "Create Risk"}
      </button>
    </form>
  );
}
