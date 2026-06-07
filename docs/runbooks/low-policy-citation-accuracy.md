# Low Policy Citation Accuracy

## Alert meaning
Investigation summaries are citing relevant policy less often than the minimum threshold.

## Severity
SEV2_MEDIUM.

## Possible causes
Retriever query mismatch, missing policy documents, prompt regression, low confidence summaries, or stale search index.

## Immediate triage steps
Compare recent case summaries with retrieved policy references and validate common policy queries.

## KQL queries to run
Run `monitoring/kql/low-policy-citation-accuracy.kql`.

## Application logs to check
Inspect `POLICY_CITATION_ACCURACY_CALCULATED`, `RAG_RETRIEVAL_COMPLETED`, and `RAG_EMPTY_RESULT`.

## Azure resources to inspect
Azure AI Search index, policy document storage, backend config, and Application Insights.

## Safe mitigation steps
Refresh policy ingestion, tune retrieval keywords, require manual policy review, or revert prompt changes.

## Escalation path
AI governance owner and fraud policy owner.

## When to resolve
Resolve after citation rate is above threshold for a representative case sample.

## Post-incident review notes
Capture failed cases, policy gaps, and evaluation updates.
