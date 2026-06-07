import { CardFrame } from "@/components/cases/CardFrame";
import type { SimilarCase } from "@/types/agent.types";

type SimilarCasesPanelProps = {
  cases: SimilarCase[];
};

export function SimilarCasesPanel({ cases }: SimilarCasesPanelProps) {
  return (
    <CardFrame title="Similar Historical Cases" subtitle="Synthetic case matches by overlapping risk indicators.">
      {cases.length === 0 ? (
        <div className="empty-state">No similar historical cases found.</div>
      ) : (
        <div className="panel-list">
          {cases.map((item) => (
            <div className="panel-item" key={item.case_id}>
              <h4>{item.case_id} - {item.outcome}</h4>
              <p>{item.summary}</p>
              <p>Matched indicators: {item.matched_risk_indicators.join(", ")}</p>
              <div className="meta-row">
                {item.source_filename && <span>{item.source_filename}</span>}
                <span>Similarity {item.similarity_score.toFixed(2)}</span>
                {item.citation?.retrieval_mode && <span>{item.citation.retrieval_mode}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
