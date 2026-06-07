from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"X-Demo-User": "manager", "X-Demo-Role": "FRAUD_MANAGER"}
ROOT = Path(__file__).resolve().parents[3]
COST_STORE = ROOT / "data" / "synthetic" / "cost_records.json"


@pytest.fixture(autouse=True)
def preserve_cost_store():
    original = COST_STORE.read_text(encoding="utf-8") if COST_STORE.exists() else '{"token_usage_records":[],"cost_records":[]}'
    yield
    COST_STORE.write_text(original, encoding="utf-8")


def test_cost_routes_return_expected_shapes() -> None:
    assert client.get("/api/v1/cost/health", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/summary", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/token-usage", headers=HEADERS).json()["records"]
    assert client.get("/api/v1/cost/cases/case-001", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/agents", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/models", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/trends/daily?days=30", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/top-cases", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/budget/status", headers=HEADERS).status_code == 200
    assert client.get("/api/v1/cost/anomalies", headers=HEADERS).status_code == 200


def test_cost_recalculate_endpoint_updates_cost_records() -> None:
    response = client.post("/api/v1/cost/recalculate", headers=HEADERS)

    assert response.status_code == 200
    assert response.json()["records_processed"] >= 1
