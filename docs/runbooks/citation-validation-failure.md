# Citation Validation Failure

## Alert meaning
The system produced or received policy citations that failed validation.

## Severity
SEV1_HIGH.

## Possible causes
RAG returned stale snippets, model output invented citations, policy source moved, or validation rules changed.

## Immediate triage steps
Review the failing summary, citation source filenames, and retrieved policy snippets.

## KQL queries to run
Run `monitoring/kql/citation-validation-failure.kql`.

## Application logs to check
Inspect `CITATION_VALIDATION_FAILED`, `RAG_RETRIEVAL_COMPLETED`, and `LLM_OUTPUT_VALIDATION_FAILED`.

## Azure resources to inspect
Azure AI Search index, policy storage source, backend deployment, and Application Insights traces.

## Safe mitigation steps
Require human-only review, disable citation-dependent recommendations, and refresh policy ingestion.

## Escalation path
AI governance owner and fraud policy owner.

## When to resolve
Resolve after citations validate against current policy documents for sample investigations.

## Post-incident review notes
Document invalid citation examples and prompt or retriever changes.
