export function formatTokens(value: number) {
  return new Intl.NumberFormat("en-US").format(value ?? 0);
}

export function formatCost(value: number, currency = "USD", digits = 6) {
  return `${currency} ${(value ?? 0).toFixed(digits)}`;
}

export function formatPercent(value: number) {
  return `${(value ?? 0).toFixed(1)}%`;
}
