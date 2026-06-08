from pathlib import Path

import pytest

from app.auth.current_user import AuthenticatedUser
from app.compliance.legal_hold_service import legal_hold_service
from app.schemas.legal_hold_schema import LegalHoldCreateRequest, LegalHoldReleaseRequest


ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "data" / "synthetic" / "legal_holds.json"
AUDIT = ROOT / "data" / "synthetic" / "audit_events.json"


@pytest.fixture(autouse=True)
def preserve_store():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "" for path in [STORE, AUDIT]}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def user() -> AuthenticatedUser:
    return AuthenticatedUser(user_id="compliance", roles=["COMPLIANCE_OFFICER"], primary_role="COMPLIANCE_OFFICER", auth_mode="local")


def test_legal_hold_service_create_release_and_block_check() -> None:
    hold = legal_hold_service.create_legal_hold(LegalHoldCreateRequest(case_id="case-001", reason="Synthetic review."), user())

    assert legal_hold_service.is_record_under_legal_hold("FRAUD_CASE", "case-001", "case-001") is True

    released = legal_hold_service.release_legal_hold(hold["legal_hold_id"], LegalHoldReleaseRequest(release_reason="Done."), user())
    assert released["status"] == "RELEASED"
