# Azure AI Search Production RAG

This MVP keeps retrieval local by default and adds an Azure AI Search-ready path for policy, historical case, and case evidence retrieval.

## Runtime Modes

Local mode requires no Azure resources:

```env
USE_AZURE_SEARCH=false
```

Azure mode uses Azure AI Search REST APIs when the endpoint and query or admin key are configured:

```env
USE_AZURE_SEARCH=true
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_QUERY_KEY=<secure value>
AZURE_SEARCH_ADMIN_KEY=<secure value>
AZURE_SEARCH_POLICY_INDEX=fraud-policies
AZURE_SEARCH_HISTORICAL_CASE_INDEX=historical-fraud-cases
AZURE_SEARCH_EVIDENCE_INDEX=case-evidence
```

Do not commit keys. Use Key Vault, pipeline secrets, or managed configuration for deployed environments.

## Source Documents

Azure ingestion source folders:

- `rag/documents/policies/`
- `rag/documents/historical_cases/`
- `rag/documents/sops/`

Local investigation fallback still reads `rag/sample_documents/policies/` and `data/synthetic/historical_cases.json`.

## Index Management

Create or update index schemas:

```bash
python -m rag.indexes.create_indexes
```

Reset indexes:

```bash
python -m rag.indexes.reset_indexes --confirm
```

Delete indexes:

```bash
python -m rag.indexes.delete_indexes --confirm
```

## Ingestion

Policy documents:

```bash
python -m rag.ingestion.ingest_policy_documents --input rag/documents/policies
```

Historical cases:

```bash
python -m rag.ingestion.ingest_historical_cases --input rag/documents/historical_cases
```

Synthetic case evidence:

```bash
python -m rag.ingestion.ingest_case_evidence --input data/synthetic
```

Embeddings are disabled by default. To enable Azure OpenAI embeddings, set:

```env
USE_AZURE_OPENAI_EMBEDDINGS=true
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_API_KEY=<secure value>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

## Backend APIs

- `GET /api/v1/rag/health`
- `POST /api/v1/rag/search/policies`
- `POST /api/v1/rag/search/historical-cases`
- `POST /api/v1/rag/search/case-evidence`
- `POST /api/v1/rag/search/all`

Responses include source filenames, matched sections, scores, retrieval mode, and citation metadata.

## Agent Grounding

`PolicyRagAgent` returns policy citations and source counts. `HistoricalCaseAgent` returns citation metadata for similar synthetic cases. `CaseSummaryAgent` records grounding counts in the investigation summary, and `ReviewerAgent` flags unsupported high-impact recommendations when policy citations are missing.
