export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatDuration(seconds: number): string {
  if (!seconds) {
    return "0s";
  }
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  return `${(seconds / 60).toFixed(1)}m`;
}

export function entries(record: Record<string, number>): Array<[string, number]> {
  return Object.entries(record).filter(([, value]) => value > 0);
}
