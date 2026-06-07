import argparse
import json
import urllib.parse
import urllib.request

from rag.config.rag_config import rag_config


def delete_indexes(confirm: bool = False) -> dict:
    if not confirm:
        return {"deleted": [], "warning": "Pass --confirm to delete indexes."}
    if not rag_config.azure_search_endpoint or not rag_config.azure_search_admin_key:
        return {"deleted": [], "warning": "Azure Search endpoint/admin key not configured."}
    deleted = []
    for name in [rag_config.policy_index, rag_config.historical_case_index, rag_config.evidence_index]:
        url = f"{rag_config.azure_search_endpoint}/indexes/{urllib.parse.quote(name)}?api-version=2024-07-01"
        request = urllib.request.Request(url, headers={"api-key": rag_config.azure_search_admin_key}, method="DELETE")
        with urllib.request.urlopen(request, timeout=30):
            deleted.append(name)
    return {"deleted": deleted}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true")
    print(json.dumps(delete_indexes(parser.parse_args().confirm), indent=2))
