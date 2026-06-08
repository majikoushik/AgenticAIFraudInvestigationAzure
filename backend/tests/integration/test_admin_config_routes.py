from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
ADMIN_HEADERS = {"X-Demo-User": "admin_user", "X-Demo-Role": "ADMIN"}
ANALYST_HEADERS = {"X-Demo-User": "analyst", "X-Demo-Role": "FRAUD_ANALYST"}
ROOT = Path(__file__).resolve().parents[3]
STORES = [
    ROOT / "data" / "synthetic" / "admin_config.json",
    ROOT / "data" / "synthetic" / "admin_config_history.json",
]


@pytest.fixture(autouse=True)
def preserve_admin_config_stores():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "{}" for path in STORES}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def test_admin_config_routes_require_admin() -> None:
    response = client.get("/api/v1/admin/config", headers=ANALYST_HEADERS)

    assert response.status_code == 403


def test_admin_config_read_update_history_health_and_reset() -> None:
    read = client.get("/api/v1/admin/config", headers=ADMIN_HEADERS)
    update = client.patch("/api/v1/admin/config", headers=ADMIN_HEADERS, json={"updates": [{"key": "RAG_TOP_K", "value": 8}], "comment": "test"})
    history = client.get("/api/v1/admin/config/history?key=RAG_TOP_K", headers=ADMIN_HEADERS)
    health = client.get("/api/v1/admin/config/health", headers=ADMIN_HEADERS)
    category = client.get("/api/v1/admin/config/RAG", headers=ADMIN_HEADERS)
    reset = client.post("/api/v1/admin/config/reset", headers=ADMIN_HEADERS, json={"comment": "reset"})

    assert read.status_code == 200
    assert update.status_code == 200
    assert update.json()["updated_count"] == 1
    assert history.json()[0]["key"] == "RAG_TOP_K"
    assert health.json()["secret_values_redacted"] is True
    assert category.json()["category"] == "RAG"
    assert reset.json()["reset_count"] >= 1


def test_admin_config_invalid_update_returns_validation_errors() -> None:
    response = client.patch("/api/v1/admin/config", headers=ADMIN_HEADERS, json={"updates": [{"key": "RAG_TOP_K", "value": 100}]})

    assert response.status_code == 200
    assert response.json()["failed_count"] == 1
