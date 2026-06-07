import json
import urllib.parse
import urllib.request

from rag.config.rag_config import rag_config
from rag.indexes.case_evidence_index_schema import build_case_evidence_index_schema
from rag.indexes.historical_case_index_schema import build_historical_case_index_schema
from rag.indexes.policy_index_schema import build_policy_index_schema


def create_indexes() -> dict:
    if not rag_config.azure_search_endpoint or not rag_config.azure_search_admin_key:
        return {"created": [], "skipped": ["Azure Search endpoint/admin key not configured."]}
    schemas = [
        build_policy_index_schema(rag_config.policy_index),
        build_historical_case_index_schema(rag_config.historical_case_index),
        build_case_evidence_index_schema(rag_config.evidence_index),
    ]
    created = []
    for schema in schemas:
        _put_index(schema)
        created.append(schema["name"])
    return {"created": created, "skipped": []}


def _put_index(schema: dict) -> None:
    name = urllib.parse.quote(schema["name"])
    url = f"{rag_config.azure_search_endpoint}/indexes/{name}?api-version=2024-07-01"
    request = urllib.request.Request(
        url,
        data=json.dumps(schema).encode("utf-8"),
        headers={"Content-Type": "application/json", "api-key": rag_config.azure_search_admin_key},
        method="PUT",
    )
    with urllib.request.urlopen(request, timeout=30):
        pass


if __name__ == "__main__":
    print(json.dumps(create_indexes(), indent=2))
