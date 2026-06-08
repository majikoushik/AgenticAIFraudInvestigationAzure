export function ConfigResetPanel({ onReset }: { onReset: () => Promise<void> }) {
  return (
    <section className="panel">
      <h2>Reset Local Overrides</h2>
      <p className="caption">This resets local non-secret overrides only. Environment variables and secrets are not changed.</p>
      <button className="button secondary" type="button" onClick={() => { if (window.confirm("Reset local admin config overrides?")) void onReset(); }}>Reset to defaults</button>
    </section>
  );
}
