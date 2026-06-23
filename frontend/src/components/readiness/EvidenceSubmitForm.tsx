"use client";

import { useState } from "react";

import { addEvidence } from "@/services/readinessService";

interface Props {
  assessmentId: string;
  checkId?: string;
  onAdded?: () => void;
}

const EVIDENCE_TYPES = ["TEXT", "FILE_REFERENCE", "URL", "CHECK_OUTPUT"] as const;

export function EvidenceSubmitForm({ assessmentId, checkId, onAdded }: Props) {
  const [checkIdInput, setCheckIdInput] = useState(checkId ?? "");
  const [evidenceType, setEvidenceType] = useState<"TEXT" | "FILE_REFERENCE" | "URL" | "CHECK_OUTPUT">("TEXT");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!checkIdInput.trim() || !description.trim()) return;
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await addEvidence(assessmentId, {
        check_id: checkIdInput.trim(),
        evidence_type: evidenceType,
        description: description.trim(),
      });
      setSuccess(true);
      setDescription("");
      onAdded?.();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to submit evidence");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="evidence-form" onSubmit={handleSubmit} aria-label="Submit evidence form">
      <h4 className="evidence-form__title">Add Manual Evidence</h4>

      {error && <div className="readiness-error">{error}</div>}
      {success && <div className="readiness-success">Evidence submitted successfully.</div>}

      <div className="form-group">
        <label htmlFor="ev-check-id" className="form-label">Check ID</label>
        <input
          id="ev-check-id"
          type="text"
          className="form-input"
          value={checkIdInput}
          onChange={(e) => setCheckIdInput(e.target.value)}
          placeholder="e.g. SEC-001"
          required
          disabled={!!checkId}
        />
      </div>

      <div className="form-group">
        <label htmlFor="ev-type" className="form-label">Evidence Type</label>
        <select
          id="ev-type"
          className="form-select"
          value={evidenceType}
          onChange={(e) => setEvidenceType(e.target.value as typeof evidenceType)}
        >
          {EVIDENCE_TYPES.map((t) => (
            <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="ev-description" className="form-label">Description / Evidence</label>
        <textarea
          id="ev-description"
          className="form-textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe the evidence, paste a URL, or provide check output..."
          rows={4}
          required
        />
      </div>

      <button
        id="btn-submit-evidence"
        type="submit"
        disabled={loading}
        className="btn btn--primary"
      >
        {loading ? "Submitting..." : "Submit Evidence"}
      </button>
    </form>
  );
}
