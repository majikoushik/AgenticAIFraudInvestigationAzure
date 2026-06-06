import { getBackendHealth } from "@/services/backend";

export async function HealthStatus() {
  const health = await getBackendHealth();

  return (
    <>
      <h2>Backend Status</h2>
      <div className="status-row">
        <span>{health.service}</span>
        <span className="badge">{health.status}</span>
      </div>
    </>
  );
}
