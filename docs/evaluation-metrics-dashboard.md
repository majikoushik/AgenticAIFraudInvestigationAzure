# Evaluation Metrics Dashboard

The evaluation metrics dashboard measures whether the agentic fraud investigation MVP is useful, trusted, evidence-supported, policy-grounded, and operationally healthy.

## Why Metrics Matter

AI recommendations in banking fraud investigation must be evaluated continuously. Human agreement, override behavior, policy citation coverage, review timing, and audit activity help determine whether the system is improving investigator productivity without weakening governance.

## Metric Groups

- Case status metrics: counts and percentages across the case lifecycle.
- AI recommendation metrics: recommendation distribution and missing recommendation count.
- Human decision metrics: final reviewer decision distribution.
- Human override metrics: override rate, AI-human match rate, and override pairs.
- Investigation time metrics: elapsed time between `AI_INVESTIGATION_STARTED` and `AI_INVESTIGATION_COMPLETED`.
- Human review time metrics: elapsed time between pending-review events and `HUMAN_DECISION_SUBMITTED`.
- Agent execution metrics: agent success, failure, execution counts, and average duration.
- RAG retrieval metrics: retrieval success, failure, mode distribution, result count, and top sources.
- Policy citation metrics: policy reference coverage and top cited sources.
- Audit metrics: total audit events grouped by category, type, and actor role.

## AI-Human Agreement

The backend normalizes AI recommendations and human decisions to `APPROVE`, `HOLD`, `ESCALATE`, and `REJECT`. A match is counted when both values are present and equal. An override is counted when both are present and differ.

## Override Rate

Override rate is calculated as:

```text
total_overrides / total_reviewed_cases * 100
```

The service avoids division by zero and returns `0.0` when no reviewed cases exist.

## Duration Metrics

Investigation duration is calculated from paired audit events for the same `case_id`:

```text
AI_INVESTIGATION_COMPLETED.timestamp - AI_INVESTIGATION_STARTED.timestamp
```

Human review wait time is calculated from `PENDING_HUMAN_REVIEW_SET` or status-change events to `HUMAN_DECISION_SUBMITTED`.

## RAG and Agent Metrics

Agent metrics use `AGENT_EXECUTION_COMPLETED` and `AGENT_EXECUTION_FAILED` audit events. RAG metrics use `RAG_RETRIEVAL_COMPLETED` and `RAG_RETRIEVAL_FAILED`, including local or Azure Search retrieval mode from audit metadata.

## API Endpoints

```text
GET /api/v1/metrics/summary
GET /api/v1/metrics/case-status
GET /api/v1/metrics/ai-vs-human
GET /api/v1/metrics/operations
GET /api/v1/metrics/audit
GET /api/v1/metrics/timeseries
```

Example summary response shape:

```json
{
  "case_status_metrics": {},
  "ai_recommendation_metrics": {},
  "human_decision_metrics": {},
  "human_override_metrics": {},
  "investigation_time_metrics": {},
  "human_review_time_metrics": {},
  "agent_execution_metrics": {},
  "rag_retrieval_metrics": {},
  "policy_citation_metrics": {},
  "audit_metrics": {}
}
```

## Frontend Dashboard

The frontend page is available at:

```text
http://localhost:3000/metrics
```

It displays summary cards, case status bars, AI-vs-human distributions, override pairs, operational timing, agent metrics, RAG metrics, policy citation metrics, and audit distributions.

## Future Production Improvements

- Stream audit and agent telemetry to Azure Monitor and Application Insights.
- Query event trends with Log Analytics KQL.
- Publish executive and operational Power BI dashboards.
- Add model evaluation pipelines using human feedback and override labels.
- Track drift in recommendation acceptance and policy citation patterns.
- Add Responsible AI reporting for evidence support, policy grounding, and human review outcomes.
