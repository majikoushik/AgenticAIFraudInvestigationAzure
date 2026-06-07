# RAG Empty Results

## Alert meaning
Policy retrieval returned empty results too often.

## Severity
SEV2_MEDIUM.

## Possible causes
Index ingestion failure, stale policy documents, query mismatch, Azure AI Search outage, or local policy folder misconfiguration.

## Immediate triage steps
Run a known policy query, verify sample policy files, and check recent ingestion changes.

## KQL queries to run
Run `monitoring/kql/high-rag-empty-result-rate.kql`.

## Application logs to check
Inspect `RAG_RETRIEVAL_STARTED`, `RAG_RETRIEVAL_COMPLETED`, `RAG_EMPTY_RESULT`, and `RAG_RETRIEVAL_FAILED`.

## Azure resources to inspect
Azure AI Search service, indexes, indexers, storage source, and backend environment variables.

## Safe mitigation steps
Rebuild the index, switch to local policy retrieval, lower strict filters, or pause AI-assisted recommendations.

## Escalation path
AI search owner and AI governance owner.

## When to resolve
Resolve after known policy queries return expected citations consistently.

## Post-incident review notes
Record missing documents, query gaps, and ingestion fixes.
