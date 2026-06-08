from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parents[3]
STORES = [
    ROOT / "data" / "synthetic" / "legal_holds.json",
    ROOT / "data" / "synthetic" / "retention_scan_results.json",
    ROOT / "data" / "synthetic" / "audit_events.json",
]
ADMIN_HEADERS = {"X-Demo-User": "admin_user", "X-Demo-Role": "ADMIN"}


@pytest.fixture(autouse=True)
def preserve_stores():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "" for path in STORES}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def test_legal_hold_creation_release_and_case_listing() -> None:
    created = client.post("/api/v1/legal-holds", headers=ADMIN_HEADERS, json={"case_id": "case-001", "reason": "Synthetic compliance review."})

    assert created.status_code == 200
    hold_id = created.json()["legal_hold_id"]
    assert created.json()["status"] == "ACTIVE"

    case_holds = client.get("/api/v1/cases/case-001/legal-holds", headers=ADMIN_HEADERS)
    assert len(case_holds.json()) == 1

    released = client.post(f"/api/v1/legal-holds/{hold_id}/release", headers=ADMIN_HEADERS, json={"release_reason": "Synthetic release."})
    assert released.status_code == 200
    assert released.json()["status"] == "RELEASED"
