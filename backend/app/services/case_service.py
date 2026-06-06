from app.repositories.case_repository import CaseRepository
from app.schemas.case_schema import CaseDetail, CaseMetadata, CaseSummary
from app.schemas.decision_schema import DecisionRequest, DecisionResponse
from app.services.audit_service import AuditService
from app.services.errors import ApiError
from app.services.evidence_service import EvidenceService
from app.services.fraud_alert_service import FraudAlertService


VALID_DECISIONS = {"approve", "hold", "escalate", "reject"}


class CaseService:
    def __init__(self, repository: CaseRepository, audit_service: AuditService) -> None:
        self.repository = repository
        self.audit_service = audit_service
        self.evidence_service = EvidenceService(repository)
        self.fraud_alert_service = FraudAlertService(repository)

    def list_cases(self) -> list[CaseSummary]:
        return self.fraud_alert_service.list_alert_cases()

    def get_case_detail(self, case_id: str) -> CaseDetail:
        alert = self.ensure_case_exists(case_id)

        return CaseDetail(
            metadata=CaseMetadata(
                case_id=alert["case_id"],
                alert_id=alert["alert_id"],
                severity=alert["severity"],
                reason=alert["reason"],
                created_at=alert["created_at"],
            ),
            customer=self.evidence_service.build_customer_profile(alert["customer_id"]),
            suspicious_transaction=self.evidence_service.build_transaction(alert["transaction_id"]),
            beneficiary=self.evidence_service.build_beneficiary(alert.get("beneficiary_id")),
            device=self.evidence_service.build_device(alert.get("device_id")),
            initial_risk_indicators=self.evidence_service.build_risk_indicators(
                alert.get("risk_indicators", [])
            ),
            historical_cases=self.evidence_service.build_historical_cases(alert["customer_id"]),
            current_status=alert["status"],
        )

    def submit_decision(self, case_id: str, request: DecisionRequest) -> DecisionResponse:
        self.ensure_case_exists(case_id)
        normalized_decision = request.decision.strip().lower()

        if normalized_decision not in VALID_DECISIONS:
            raise ApiError(
                400,
                "invalid_decision",
                "Decision must be one of: approve, hold, escalate, reject.",
            )

        normalized_request = DecisionRequest(
            decision=normalized_decision,
            comment=request.comment,
            reviewed_by=request.reviewed_by,
        )
        self.audit_service.record_decision(case_id, normalized_request)

        return DecisionResponse(
            case_id=case_id,
            decision=normalized_decision,
            status="recorded",
            message="Human investigator decision recorded.",
        )

    def ensure_case_exists(self, case_id: str) -> dict:
        alert = self.repository.get_alert(case_id)
        if alert is None:
            raise ApiError(404, "case_not_found", f"Case '{case_id}' was not found.")

        return alert
