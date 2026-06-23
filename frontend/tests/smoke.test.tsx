import { describe, it, expect } from 'vitest';
import { maskCustomerId, formatCurrency, normalizeRiskClass } from '../src/utils/maskingUtils';

describe('Frontend Utility Smoke Test', () => {
  it('masks customer IDs correctly', () => {
    expect(maskCustomerId('123')).toBe('****');
    expect(maskCustomerId('12345678')).toBe('1234-***');
  });

  it('formats currency properly', () => {
    const formatted = formatCurrency(1234.5, 'USD');
    expect(formatted).toContain('1,234.50');
    expect(formatted).toContain('$');
  });

  it('normalizes risk class', () => {
    expect(normalizeRiskClass('HIGH')).toBe('risk-high');
    expect(normalizeRiskClass('unknown')).toBe('risk-medium');
  });
});
