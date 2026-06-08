from pathlib import Path

import pytest

from app.compliance.compliance_export_service import compliance_export_service


ROOT = Path(__file__).resolve().parents[3]
STORES = [
    ROOT / "data" / "synthetic" / "compliance_exports.json",
    ROOT / "data" / "synthetic" / "audit_events.json",
]


@pytest.fixture(autouse=True)
def preserve_store():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "" for path in STORES}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def test_compliance_export_service_creates_sanitized_export() -> None:
    export = compliance_export_service.create_case_compliance_export("case-001", "tester", {"redact_pii": True, "include_audit": True, "include_feedback": True, "include_ai_outputs": True})

    assert export["status"] == "COMPLETED"
    assert export["manifest"]["redaction_applied"] is True
