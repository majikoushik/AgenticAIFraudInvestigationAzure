import type { FeatureFlag } from "@/types/adminConfig.types";

export function FeatureFlagPanel({ flags, onToggle }: { flags: FeatureFlag[]; onToggle: (flag: FeatureFlag, enabled: boolean) => Promise<void> }) {
  return (
    <section className="panel">
      <h2>Feature Flags</h2>
      <div className="stack">
        {flags.map((flag) => (
          <label className="checkbox-row" key={flag.key}>
            <input checked={Boolean(flag.value)} type="checkbox" onChange={(event) => void onToggle(flag, event.target.checked)} />
            <span><strong>{flag.key}</strong><br />{flag.description}</span>
          </label>
        ))}
      </div>
    </section>
  );
}
