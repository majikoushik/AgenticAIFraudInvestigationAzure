export function PricingConfigWarning({ configured }: { configured: boolean }) {
  if (configured) return null;
  return (
    <div className="notice warning">
      Pricing values are not configured. Cost values are shown as 0. Configure token pricing environment variables for estimated cost.
    </div>
  );
}
