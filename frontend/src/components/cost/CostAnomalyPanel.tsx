import type { CostAnomaly } from "@/types/cost.types";

export function CostAnomalyPanel({ anomalies }: { anomalies: CostAnomaly[] }) {
  return (
    <section className="panel">
      <h2>Cost Anomalies</h2>
      <div className="stack">
        {anomalies.map((item) => (
          <div className="row" key={item.anomaly_type}>
            <span>{item.anomaly_type}</span>
            <strong>{item.status}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
