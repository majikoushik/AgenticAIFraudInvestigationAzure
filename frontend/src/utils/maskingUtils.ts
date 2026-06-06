export function maskCustomerId(customerId: string): string {
  if (customerId.length <= 4) {
    return "****";
  }
  return `${customerId.slice(0, 4)}-***`;
}

export function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency
  }).format(amount);
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export function normalizeRiskClass(value: string): string {
  const normalized = value.toLowerCase();
  if (["low", "medium", "high", "critical"].includes(normalized)) {
    return `risk-${normalized}`;
  }
  return "risk-medium";
}
