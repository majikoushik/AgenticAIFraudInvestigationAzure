import { CardFrame } from "@/components/cases/CardFrame";
import type { InvestigationSummary } from "@/types/agent.types";
import type { RiskIndicator } from "@/types/case.types";
import { normalizeRiskClass } from "@/utils/maskingUtils";

type RiskIndicatorPanelProps = {
  title: string;
  indicators: RiskIndicator[];
  summary?: InvestigationSummary;
};

export function RiskIndicatorPanel({ title, indicators, summary }: RiskIndicatorPanelProps) {
  return (
    <CardFrame title={title} subtitle={summary ? "Structured output from the local agent workflow." : "Risk signals loaded from the case alert."} fullSpan={Boolean(summary)}>
      <div className="stack">
        {summary && (
          <div className="panel-item">
            <h4>Recommended action: {summary.recommended_action}</h4>
            <p>Confidence: {summary.confidence_level}. {summary.case_overview}</p>
          </div>
        )}
        {indicators.length === 0 ? (
          <div className="empty-state">No risk indicators available.</div>
        ) : (
          <div className="panel-list">
            {indicators.map((indicator) => (
              <div className="panel-item" key={indicator.code}>
                <h4>
                  {indicator.code} <span className={`badge ${normalizeRiskClass(indicator.severity)}`}>{indicator.severity}</span>
                </h4>
                <p>{indicator.description}</p>
              </div>
            ))}
          </div>
        )}
        {summary && (
          <div className="panel-list">
            <div className="panel-item">
              <h4>Evidence supporting suspicion</h4>
              <p>{summary.evidence_supporting_suspicion.join(" ") || "No supporting evidence listed."}</p>
            </div>
            <div className="panel-item">
              <h4>Evidence reducing suspicion</h4>
              <p>{summary.evidence_reducing_suspicion.join(" ") || "No reducing evidence listed."}</p>
            </div>
            <div className="panel-item">
              <h4>Missing evidence</h4>
              <p>{summary.missing_evidence.join(" ") || "No missing evidence identified."}</p>
            </div>
          </div>
        )}
      </div>
    </CardFrame>
  );
}
