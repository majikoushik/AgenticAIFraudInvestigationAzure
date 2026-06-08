from pathlib import Path

import pytest

from app.auth.current_user import AuthenticatedUser
from app.compliance.legal_hold_service import legal_hold_service
from app.compliance.purge_service import purge_service
from app.schemas.legal_hold_schema import LegalHoldCreateRequest
from app.services.errors import ApiError


ROOT = Path(__file__).resolve().parents[3]
STORES = [
    ROOT / "data" / "synthetic" / "legal_holds.json",
    ROOT / "data" / "synthetic" / "audit_events.json",
]


@pytest.fixture(autouse=True)
def preserve_store():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "" for path in STORES}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def user() -> AuthenticatedUser:
    return AuthenticatedUser(user_id="compliance", roles=["COMPLIANCE_OFFICER"], primary_role="COMPLIANCE_OFFICER", auth_mode="local")


def test_purge_dry_run_and_approval_requirement() -> None:
    dry_run = purge_service.purge_record("FRAUD_CASE", "case-001", "tester", dry_run=True)
    assert dry_run["dry_run"] is True
    with pytest.raises(ApiError):
        purge_service.purge_record("FRAUD_CASE", "case-001", "tester", dry_run=False)


def test_purge_blocked_when_legal_hold_active() -> None:
    legal_hold_service.create_legal_hold(LegalHoldCreateRequest(case_id="case-001", reason="Synthetic review."), user())
    result = purge_service.purge_record("FRAUD_CASE", "case-001", "tester", dry_run=True)

    assert result["blocked_count"] == 1
