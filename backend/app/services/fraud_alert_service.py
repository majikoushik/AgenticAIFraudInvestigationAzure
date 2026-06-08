from app.repositories.case_repository import CaseRepository
from app.assignment.assignment_repository import normalize_assignment_fields
from app.schemas.case_schema import CaseSummary
from app.schemas.assignment_schema import AssignmentFields
from app.services.case_status_service import CaseStatusService


class FraudAlertService:
    def __init__(self, repository: CaseRepository, status_service: CaseStatusService) -> None:
        self.repository = repository
        self.status_service = status_service

    def list_alert_cases(self) -> list[CaseSummary]:
        return [
            CaseSummary(
                case_id=alert["case_id"],
                alert_id=alert["alert_id"],
                customer_id=alert["customer_id"],
                severity=alert["severity"],
                status=self.status_service.get_status(alert["case_id"], alert.get("status")).value,
                status_updated_at=alert.get("status_updated_at"),
                status_updated_by=alert.get("status_updated_by"),
                status_comment=alert.get("status_comment"),
                reason=alert["reason"],
                created_at=alert["created_at"],
                assignment=AssignmentFields(**{
                    key: normalize_assignment_fields(alert).get(key)
                    for key in AssignmentFields.model_fields
                }),
            )
            for alert in self.repository.list_alerts()
        ]
