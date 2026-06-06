import json
import os
from pathlib import Path
import urllib.error
import urllib.request


API_VERSION = "2024-07-01"


def main() -> None:
    endpoint = required_env("AZURE_SEARCH_ENDPOINT").rstrip("/")
    admin_key = required_env("AZURE_SEARCH_ADMIN_KEY")
    policy_index = os.getenv("AZURE_SEARCH_POLICY_INDEX", "fraud-policies")
    case_index = os.getenv("AZURE_SEARCH_CASE_INDEX", "historical-fraud-cases")
    schema_dir = Path(__file__).resolve().parent

    create_or_update_index(endpoint, admin_key, policy_index, schema_dir / "policy_index_schema.json")
    create_or_update_index(endpoint, admin_key, case_index, schema_dir / "historical_case_index_schema.json")
    print("Azure AI Search index creation completed.")


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def create_or_update_index(endpoint: str, admin_key: str, index_name: str, schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["name"] = index_name
    url = f"{endpoint}/indexes/{index_name}?api-version={API_VERSION}"
    request = urllib.request.Request(
        url,
        data=json.dumps(schema).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "api-key": admin_key,
        },
        method="PUT",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response.read()
            print(f"Created or updated index: {index_name}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to create or update index {index_name}: {exc}") from exc


if __name__ == "__main__":
    main()
