# Data Retention and Compliance Policy

This MVP defines a local JSON-backed data retention, archival, purge, legal hold, and compliance export framework for the fraud investigation platform.

The default retention periods are placeholders. They are not legal advice and must be reviewed and approved by legal/compliance before production use.

## Data Categories and Classification

The backend defines `DataCategory`, `DataClassification`, `RetentionAction`, `RetentionStatus`, `LegalHoldStatus`, and `ComplianceExportStatus` in `backend/app/core/constants.py`.

Restricted categories include fraud cases, audit events, human review, AI investigation output, incidents, and export files. Confidential categories include agent trace, RAG retrieval records, feedback, notifications, config history, and assignment history. Cost and telemetry are internal by default.

## Policy Model

Retention policies include retention days, archive days, purge days, approval requirements, legal hold behavior, and whether purge is allowed. Local overrides are stored in `data/synthetic/retention_policies.json`.

## Archive Workflow

Retention scans identify archive candidates when records pass the archive threshold. Archive actions default to dry run. Non-dry-run archive copies records to `data/archive/{data_category}/{year}/{record_id}.json` and marks retention metadata where practical.

## Purge Workflow

Purge defaults to dry run through `PURGE_DRY_RUN_DEFAULT=true`. A real purge requires `dry_run=false`; when `RETENTION_REQUIRE_APPROVAL_FOR_PURGE=true`, an `approval_id` is also required. Audit events are protected from purge unless the policy explicitly allows purge.

## Legal Holds

Legal holds can target a case, record, or category. Active legal holds block purge. Creation and release are audited and exposed through `/api/v1/legal-holds`.

## Compliance Exports

Case exports are written under `data/exports/compliance/{case_id}/{export_id}.json`. Exports include a manifest, sanitized case details, legal hold status, selected audit records, feedback records, and a statement that raw prompts, raw model responses, and chain-of-thought are excluded.

## Redaction

Compliance redaction masks PII-like values such as account numbers, emails, phone-like numbers, raw prompts, raw responses, tokens, secrets, authorization headers, API keys, passwords, and connection strings.

## Roles

`ADMIN` can perform all actions. `COMPLIANCE_OFFICER` can manage policies, legal holds, scans, exports, archive, and protected purge. `AUDITOR` can view summaries, policies, legal holds, and exports. `FRAUD_MANAGER` can view compliance context but cannot purge.

## API Examples

Run dry-run scan:

```bash
curl -X POST http://localhost:8000/api/v1/retention/scan -H "Content-Type: application/json" -d '{"dry_run": true}'
```

Create legal hold:

```bash
curl -X POST http://localhost:8000/api/v1/legal-holds -H "Content-Type: application/json" -d '{"case_id":"case-001","reason":"Regulatory investigation in progress."}'
```

Create export:

```bash
curl -X POST http://localhost:8000/api/v1/compliance/exports/case/case-001 -H "Content-Type: application/json" -d '{"redact_pii": true}'
```

## Azure Production Design

Use Blob lifecycle management for archive/export containers, immutable blob storage where required, legal hold controls for compliance packages, Cosmos DB TTL per container only after approval, Microsoft Purview data map integration, Key Vault for secrets, and managed identity/RBAC for storage access.

## Future Improvements

Add dual-control purge approval, ServiceNow or Jira compliance tickets, scheduled scans, immutable audit store, automated compliance reporting, jurisdiction-specific profiles, and Microsoft Purview classification sync.
