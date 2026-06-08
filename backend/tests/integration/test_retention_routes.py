from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parents[3]
STORES = [
    ROOT / "data" / "synthetic" / "retention_policies.json",
    ROOT / "data" / "synthetic" / "retention_scan_results.json",
    ROOT / "data" / "synthetic" / "audit_events.json",
]
ADMIN_HEADERS = {"X-Demo-User": "admin_user", "X-Demo-Role": "ADMIN"}
ANALYST_HEADERS = {"X-Demo-User": "analyst", "X-Demo-Role": "FRAUD_ANALYST"}


@pytest.fixture(autouse=True)
def preserve_stores():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "" for path in STORES}
    yield
    for path, content in originals.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_retention_routes_scan_and_review_queue() -> None:
    policies = client.get("/api/v1/retention/policies", headers=ADMIN_HEADERS)
    scan = client.post("/api/v1/retention/scan", headers=ADMIN_HEADERS, json={"dry_run": True})
    queue = client.get("/api/v1/retention/review-queue", headers=ADMIN_HEADERS)

    assert policies.status_code == 200
    assert scan.status_code == 200
    assert scan.json()["dry_run"] is True
    assert "records_scanned" in scan.json()
    assert queue.status_code == 200


def test_retention_routes_enforce_permissions() -> None:
    response = client.post("/api/v1/retention/scan", headers=ANALYST_HEADERS, json={"dry_run": True})

    assert response.status_code == 403
