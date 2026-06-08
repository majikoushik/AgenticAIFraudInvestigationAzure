from pathlib import Path

import pytest

from app.compliance.retention_scanner import retention_scanner


ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "data" / "synthetic" / "retention_scan_results.json"
AUDIT = ROOT / "data" / "synthetic" / "audit_events.json"


@pytest.fixture(autouse=True)
def preserve_store():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "" for path in [STORE, AUDIT]}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def test_retention_scanner_runs_dry_run() -> None:
    scan = retention_scanner.scan_category("FRAUD_CASE", dry_run=True)

    assert scan["dry_run"] is True
    assert scan["records_scanned"] >= 1
    assert "candidates" in scan
