from app.repositories.case_repository import CaseRepository
from app.schemas.case_schema import CaseSummary


class FraudAlertService:
    def __init__(self, repository: CaseRepository) -> None:
        self.repository = repository

    def list_alert_cases(self) -> list[CaseSummary]:
        return [
            CaseSummary(
                case_id=alert["case_id"],
                alert_id=alert["alert_id"],
                customer_id=alert["customer_id"],
                severity=alert["severity"],
                status=alert["status"],
                reason=alert["reason"],
                created_at=alert["created_at"],
            )
            for alert in self.repository.list_alerts()
        ]
