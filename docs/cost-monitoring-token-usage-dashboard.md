# Cost Monitoring And Token Usage Dashboard

This MVP adds local estimated cost monitoring for LLM and agent token usage. It does not call Azure Cost Management by default and does not require Azure credentials.

## Estimated Cost Vs Azure Billing

Local cost values are estimates calculated from captured token counts and configured token rates. Azure billing cost can differ because of model pricing changes, regional pricing, provisioned throughput, reservations, retries, non-LLM resources, taxes, discounts, and billing latency.

## Token Usage Model

Token usage records store counts and operational metadata only: case ID, agent name, operation name, provider, model or deployment, token counts, RAG context estimate, retry/fallback flags, success state, and error type.

Raw prompts, raw model responses, chain-of-thought, JWTs, API keys, and PII are not stored.

## Cost Estimation Formula

Input cost: `(prompt_tokens / 1000) * input_token_cost_per_1k`

Output cost: `(completion_tokens / 1000) * output_token_cost_per_1k`

Total estimated cost: `estimated_input_cost + estimated_output_cost`

Costs are rounded to 6 decimal places.

## Pricing Configuration

Pricing defaults to `0.0000` so the MVP does not embed pricing assumptions. Configure pricing through environment variables or secure pipeline variables.

When all rates are zero, the frontend shows a pricing warning and estimated costs remain `0`.

## Backend APIs

- `GET /api/v1/cost/health`
- `GET /api/v1/cost/summary`
- `GET /api/v1/cost/token-usage`
- `GET /api/v1/cost/cases/{case_id}`
- `GET /api/v1/cost/agents`
- `GET /api/v1/cost/models`
- `GET /api/v1/cost/trends/daily?days=30`
- `GET /api/v1/cost/top-cases?limit=10`
- `GET /api/v1/cost/budget/status`
- `GET /api/v1/cost/anomalies`
- `POST /api/v1/cost/recalculate`
- `GET /api/v1/cost/azure/placeholder?start_date=2026-06-01&end_date=2026-06-30`
- `GET /api/v1/cost/export/summary.csv`

## Dashboard

The frontend dashboard is available at `/cost` and shows total tokens, estimated cost, cost by agent, cost by model, top expensive cases, budget status, anomaly indicators, and pricing configuration warning.

## Budget Monitoring

Budget status uses configured local thresholds:

```env
COST_DAILY_BUDGET_LIMIT=50
COST_MONTHLY_BUDGET_LIMIT=1000
TOKEN_DAILY_LIMIT=1000000
TOKEN_PER_CASE_WARNING_THRESHOLD=25000
COST_PER_CASE_WARNING_THRESHOLD=2.00
```

If a limit is zero, the relevant budget check returns `NOT_CONFIGURED`.

## Cost Anomaly Detection

The MVP compares current daily cost or token usage against the average of the previous configured baseline days. If there is insufficient baseline data, anomaly checks return `NOT_ENOUGH_DATA`.

## Azure Cost Management Placeholder

Azure Cost Management is disabled by default. The placeholder client returns a clear disabled message. Production integration should use managed identity and must not expose secrets.

## Local Verification

1. Start the backend.
2. Call `POST /api/v1/cost/recalculate` to estimate costs from sample token records.
3. Open `http://localhost:3000/cost`.
4. Confirm token totals, agent/model tables, budget status, and pricing warning.

## Security And Privacy

- Do not store raw prompts.
- Do not store raw model responses.
- Do not store chain-of-thought.
- Do not store JWT tokens.
- Do not store API keys.
- Sanitize token usage and cost metadata.
- Treat cost values as estimated unless Azure billing integration is enabled.

## Future Improvements

- Azure Cost Management API integration
- Azure Monitor budget alerts
- Power BI cost dashboard
- per-user cost attribution
- chargeback/showback by team
- prompt optimization recommendations
- model routing based on cost/performance
- cache hit rate and cost savings dashboard
