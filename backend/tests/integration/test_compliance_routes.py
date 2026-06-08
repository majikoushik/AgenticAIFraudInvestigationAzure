from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parents[3]
STORES = [
    ROOT / "data" / "synthetic" / "compliance_exports.json",
    ROOT / "data" / "synthetic" / "audit_events.json",
]
EXPORT_ROOT = ROOT / "data" / "exports" / "compliance"
ADMIN_HEADERS = {"X-Demo-User": "admin_user", "X-Demo-Role": "ADMIN"}
AUDITOR_HEADERS = {"X-Demo-User": "auditor", "X-Demo-Role": "AUDITOR"}


@pytest.fixture(autouse=True)
def preserve_stores():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "" for path in STORES}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def test_compliance_summary_and_export() -> None:
    summary = client.get("/api/v1/compliance/summary", headers=AUDITOR_HEADERS)
    export = client.post("/api/v1/compliance/exports/case/case-001", headers=ADMIN_HEADERS, json={"redact_pii": True})

    assert summary.status_code == 200
    assert "compliance_warnings" in summary.json()
    assert export.status_code == 200
    payload = export.json()
    assert payload["status"] == "COMPLETED"
    assert payload["manifest"]["redaction_applied"] is True
