"use client";

import type { ReadinessCategoryResult } from "@/types/readiness.types";

interface Props {
  categoryResults: ReadinessCategoryResult[];
}

function scoreColor(score: number): string {
  if (score >= 90) return "#22c55e";
  if (score >= 70) return "#f59e0b";
  if (score >= 50) return "#f97316";
  return "#ef4444";
}

export function ReadinessCategoryScoreGrid({ categoryResults }: Props) {
  if (!categoryResults.length) {
    return <p className="readiness-empty">No category results available.</p>;
  }

  return (
    <div className="readiness-category-grid">
      {categoryResults.map((cat) => (
        <div key={cat.category} className="readiness-category-card">
          <div className="readiness-category-card__name">
            {cat.category.replace(/_/g, " ")}
          </div>
          <div
            className="readiness-category-card__score"
            style={{ color: scoreColor(cat.score) }}
          >
            {cat.score.toFixed(1)}
          </div>
          <div className="readiness-category-card__bar-bg">
            <div
              className="readiness-category-card__bar-fill"
              style={{
                width: `${cat.score}%`,
                backgroundColor: scoreColor(cat.score),
              }}
            />
          </div>
          <div className="readiness-category-card__stats">
            <span title="Pass">✅ {cat.pass_count}</span>
            <span title="Fail">❌ {cat.fail_count}</span>
            <span title="Warning">⚠️ {cat.warning_count}</span>
            <span title="Manual">🔵 {cat.manual_review_count}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
