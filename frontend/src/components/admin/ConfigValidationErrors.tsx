export function ConfigValidationErrors({ errors }: { errors: Array<{ key: string; errors: string[] }> }) {
  if (!errors.length) return null;
  return <div className="message error">{errors.map((error) => <p key={error.key}><strong>{error.key}</strong>: {error.errors.join(" ")}</p>)}</div>;
}
