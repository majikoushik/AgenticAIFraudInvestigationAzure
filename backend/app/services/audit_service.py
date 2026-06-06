from datetime import UTC, datetime

from app.schemas.decision_schema import DecisionRequest
from app.schemas.evidence_schema import AuditEntry


class AuditService:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record_decision(self, case_id: str, request: DecisionRequest) -> AuditEntry:
        entry = AuditEntry(
            case_id=case_id,
            action="decision_submitted",
            decision=request.decision,
            comment=request.comment,
            reviewed_by=request.reviewed_by,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._entries.append(entry)
        return entry

    def get_entries(self, case_id: str) -> list[AuditEntry]:
        return [entry for entry in self._entries if entry.case_id == case_id]


audit_service = AuditService()
