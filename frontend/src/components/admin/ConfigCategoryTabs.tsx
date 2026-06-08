import type { AdminConfigCategory } from "@/types/adminConfig.types";

const labels: Record<string, string> = {
  AI_PROVIDER: "AI Provider",
  AZURE_OPENAI_FOUNDRY: "Azure OpenAI / Foundry",
  RAG: "RAG",
  HUMAN_REVIEW: "Human Review",
  ALERTING: "Alerting",
  COST_MONITORING: "Cost Monitoring",
  OBSERVABILITY: "Observability",
  FEATURE_FLAGS: "Feature Flags"
};

export function ConfigCategoryTabs({ categories, active, onChange }: { categories: AdminConfigCategory[]; active: string; onChange: (value: string) => void }) {
  return (
    <div className="tab-row">
      {categories.map((category) => (
        <button className={active === category.category ? "tab active" : "tab"} key={category.category} onClick={() => onChange(category.category)} type="button">
          {labels[category.category] ?? category.category}
        </button>
      ))}
    </div>
  );
}
