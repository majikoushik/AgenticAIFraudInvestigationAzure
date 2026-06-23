"use client";

import { useState } from "react";
import { exportAssessment } from "@/services/readinessService";
import type { ReadinessReportResult } from "@/types/readiness.types";

interface Props {
  assessmentId: string;
}

export function ReadinessReportExporter({ assessmentId }: Props) {
  const [format, setFormat] = useState<"markdown" | "json">("markdown");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReadinessReportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleExport() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await exportAssessment(assessmentId, format);
      setResult(r);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Export failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="report-exporter">
      <h4 className="report-exporter__title">Export Report</h4>

      {error && <div className="readiness-error">{error}</div>}

      <div className="report-exporter__controls">
        <select
          id="rpt-format"
          value={format}
          onChange={(e) => setFormat(e.target.value as "markdown" | "json")}
          className="form-select form-select--sm"
          disabled={loading}
        >
          <option value="markdown">Markdown (.md)</option>
          <option value="json">JSON</option>
        </select>
        <button
          id="btn-export-report"
          onClick={handleExport}
          disabled={loading}
          className="btn btn--secondary btn--sm"
        >
          {loading ? "Exporting..." : "Export"}
        </button>
      </div>

      {result && (
        <div className="report-exporter__result">
          <div className="report-exporter__path">
            📄 Exported to: <code>{result.export_path}</code>
          </div>
          <div className="report-exporter__preview">
            <strong>Preview:</strong>
            <pre className="report-preview">{result.content_preview}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
