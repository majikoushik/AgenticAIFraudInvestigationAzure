import json
from datetime import UTC, datetime
from uuid import uuid4

from app.compliance.retention_config import retention_config
from app.core.constants import AuditEventType, DataCategory, LegalHoldStatus, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.schemas.legal_hold_schema import LegalHoldCreateRequest, LegalHoldReleaseRequest
from app.services.audit_service import audit_service
from app.services.errors import ApiError


class LegalHoldService:
    def __init__(self) -> None:
        self.path = retention_config.resolve_path(retention_config.legal_hold_store_path)

    def create_legal_hold(self, request: LegalHoldCreateRequest, current_user) -> dict:
        if not request.case_id and not request.record_id and not request.data_category:
            raise ApiError(400, "invalid_legal_hold", "Legal hold requires case_id, record_id, or data_category.")
        now = datetime.now(UTC)
        hold = {
            "legal_hold_id": f"LH-{now.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "case_id": request.case_id,
            "record_id": request.record_id,
            "data_category": request.data_category.value if request.data_category else None,
            "reason": request.reason,
            "created_by": current_user.user_id,
            "created_at": now.isoformat(),
            "status": LegalHoldStatus.ACTIVE.value,
            "released_by": None,
            "released_at": None,
            "release_reason": None,
            "metadata": request.metadata,
        }
        store = self._read_store()
        store["legal_holds"].append(hold)
        self._write_store(store)
        audit_service.record_event(None, AuditEventType.LEGAL_HOLD_CREATED, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"legal_hold_id": hold["legal_hold_id"], "case_id": request.case_id, "record_id": request.record_id, "data_category": hold["data_category"]})
        get_telemetry_client().track_event(telemetry_events.LEGAL_HOLD_CREATED, {"data_category": hold["data_category"] or "ANY"})
        return hold

    def release_legal_hold(self, legal_hold_id: str, request: LegalHoldReleaseRequest, current_user) -> dict:
        store = self._read_store()
        for hold in store["legal_holds"]:
            if hold["legal_hold_id"] == legal_hold_id:
                if hold["status"] != LegalHoldStatus.ACTIVE.value:
                    raise ApiError(400, "legal_hold_not_active", "Only active legal holds can be released.")
                hold.update({"status": LegalHoldStatus.RELEASED.value, "released_by": current_user.user_id, "released_at": datetime.now(UTC).isoformat(), "release_reason": request.release_reason})
                self._write_store(store)
                audit_service.record_event(None, AuditEventType.LEGAL_HOLD_RELEASED, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"legal_hold_id": legal_hold_id, "release_reason": request.release_reason})
                get_telemetry_client().track_event(telemetry_events.LEGAL_HOLD_RELEASED, {"legal_hold_id": legal_hold_id})
                return hold
        raise ApiError(404, "legal_hold_not_found", f"Legal hold {legal_hold_id} was not found.")

    def list_legal_holds(self, status: str | None = None, case_id: str | None = None) -> list[dict]:
        holds = self._read_store()["legal_holds"]
        if status:
            holds = [hold for hold in holds if hold.get("status") == status]
        if case_id:
            holds = [hold for hold in holds if hold.get("case_id") == case_id]
        return holds

    def get_legal_hold(self, legal_hold_id: str) -> dict:
        for hold in self._read_store()["legal_holds"]:
            if hold["legal_hold_id"] == legal_hold_id:
                return hold
        raise ApiError(404, "legal_hold_not_found", f"Legal hold {legal_hold_id} was not found.")

    def is_record_under_legal_hold(self, data_category: str, record_id: str, case_id: str | None = None) -> bool:
        category = DataCategory(data_category).value
        for hold in self.list_legal_holds(status=LegalHoldStatus.ACTIVE.value):
            if hold.get("record_id") and hold.get("record_id") == record_id:
                return True
            if hold.get("case_id") and (hold.get("case_id") == case_id or hold.get("case_id") == record_id):
                return True
            if hold.get("data_category") and hold.get("data_category") == category and not hold.get("record_id") and not hold.get("case_id"):
                return True
        return False

    def get_holds_for_case(self, case_id: str) -> list[dict]:
        return self.list_legal_holds(case_id=case_id)

    def _read_store(self) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_store({"legal_holds": []})
        return json.loads(self.path.read_text(encoding="utf-8") or '{"legal_holds":[]}')

    def _write_store(self, payload: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


legal_hold_service = LegalHoldService()
