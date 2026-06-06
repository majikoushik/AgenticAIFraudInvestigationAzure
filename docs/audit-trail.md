# Audit Trail

## Purpose

The audit trail records important system and human actions in the fraud investigation workflow. In banking fraud operations, auditability supports traceability, reviewer accountability, policy compliance, and post-case investigation.

## Event Schema

Audit events include:

- `audit_id`
- `case_id`
- `event_type`
- `event_category`
- `actor`
- `actor_role`
- `action`
- `description`
- status, decision, override, agent, RAG, error, correlation, and metadata fields
- timezone-aware UTC `timestamp`

Audit IDs use:

```text
AUDIT-{YYYYMMDDHHMMSS}-{short_uuid}
```

## Event Categories

- `CASE`
- `AI`
- `AGENT`
- `RAG`
- `HUMAN_REVIEW`
- `SECURITY`
- `ERROR`

## Supported Event Types

Use:

```http
GET /api/v1/audit/event-types
```

to list current event types and categories.

## Integration Points

The MVP records audit events for:

- Case status changes
- AI investigation start, completion, and failure
- Agent execution start, completion, and failure
- RAG retrieval start, completion, and failure
- Human decision submissions
- Human override detection
- Case close events
- API and security events where applicable

## Privacy Rules

Audit metadata is sanitized before storage.

Do not store:

- Full account numbers
- Raw customer identifiers when avoidable
- Raw prompts containing PII
- Full LLM reasoning traces
- API keys, tokens, or authorization headers

Store:

- Case IDs
- Source document names
- Agent names
- Status changes
- Decision metadata
- Error summaries
- Retrieval source names

## API Examples

Case audit:

```http
GET /api/v1/cases/case-001/audit
```

Search:

```http
GET /api/v1/audit/search?case_id=case-001&event_type=CASE_STATUS_CHANGED
```

Summary:

```http
GET /api/v1/audit/summary
```

## Local Storage

For the MVP, audit events are stored in:

```text
data/synthetic/audit_events.json
```

Reset local audit data by replacing file contents with:

```json
[]
```

## Future Production Considerations

- Cosmos DB audit container
- Immutable storage
- Azure Log Analytics integration
- Microsoft Sentinel analytics
- Retention policy
- RBAC and auditor access
- Tamper-resistant audit records
