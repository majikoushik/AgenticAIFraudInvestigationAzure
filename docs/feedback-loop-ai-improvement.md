# Feedback Loop for AI Improvement

The feedback loop captures investigator feedback on AI summaries, recommendations, policy citations, similar cases, risk explanations, reviewer validation, and agent traces.

Feedback is stored locally in `data/synthetic/ai_feedback.json`; improvement actions are stored in `data/synthetic/ai_improvement_backlog.json`. Accepted feedback can be exported to `data/exports/feedback_eval_dataset.json` for future regression evaluation.

## Security and Privacy

The backend sanitizer removes raw prompts, raw model responses, chain-of-thought, tokens, secrets, connection strings, account numbers, emails, and phone-like values. Evaluation exports use sanitized summaries only and require admin permission.

## Workflow

Investigators submit feedback from the case detail page after an AI investigation. Negative feedback requires a comment. Critical safety, PII, prompt-injection, or hallucination feedback creates backlog items and sends admin notifications when notifications are enabled.

## APIs

- `POST /api/v1/feedback`
- `GET /api/v1/feedback`
- `GET /api/v1/cases/{case_id}/feedback`
- `PATCH /api/v1/feedback/{feedback_id}/disposition`
- `GET /api/v1/feedback/analytics/summary`
- `GET /api/v1/feedback/backlog`
- `POST /api/v1/feedback/export/eval-dataset`

## Future Improvements

Future production work can move storage to Cosmos DB or Azure SQL, register evaluation datasets in Azure ML, integrate Azure AI Foundry evaluation, add prompt versioning, publish Power BI AI quality dashboards, and support governed fine-tuning only after approval.
