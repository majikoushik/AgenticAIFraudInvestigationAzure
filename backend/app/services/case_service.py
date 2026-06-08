from app.core.constants import AuditEventType, CaseStatus, ReviewerRole, normalize_decision
from app.assignment.assignment_repository import normalize_assignment_fields
from app.repositories.case_repository import CaseRepository
from app.schemas.assignment_schema import AssignmentFields
from app.schemas.case_schema import CaseDetail, CaseMetadata, CaseSummary
from app.schemas.decision_schema import DecisionRequest, DecisionResponse
from app.services.audit_service import AuditService
from app.services.case_status_service import CaseStatusService, case_status_service
from app.services.errors import ApiError
from app.services.evidence_service import EvidenceService
from app.services.fraud_alert_service import FraudAlertService


VALID_DECISIONS = {"approve", "hold", "escalate", "reject"}


class CaseService:
    _ai_recommendations: dict[str, str | None] = {}
    _investigation_summaries: dict[str, dict] = {}

    def __init__(
        self,
        repository: CaseRepository,
        audit_service: AuditService,
        status_service: CaseStatusService = case_status_service,
    ) -> None:
        self.repository = repository
        self.audit_service = audit_service
        self.status_service = status_service
        self.evidence_service = EvidenceService(repository)
        self.fraud_alert_service = FraudAlertService(repository, status_service)

    def list_cases(self) -> list[CaseSummary]:
        return self.fraud_alert_service.list_alert_cases()

    def get_case_detail(self, case_id: str) -> CaseDetail:
        alert = self.ensure_case_exists(case_id)
        assignment_case = normalize_assignment_fields(alert)
        current_status = self.status_service.get_status(case_id, alert.get("status"))

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
            current_status=current_status.value,
            status=current_status.value,
            status_updated_at=alert.get("status_updated_at"),
            status_updated_by=alert.get("status_updated_by"),
            status_comment=alert.get("status_comment"),
            ai_recommendation=self.get_ai_recommendation(case_id),
            investigation_summary=self._investigation_summaries.get(case_id) or alert.get("investigation_summary"),
            human_review=alert.get("human_review"),
            override_summary=alert.get("override_summary"),
            audit_events=[],
            assignment=AssignmentFields(**{
                key: assignment_case.get(key)
                for key in AssignmentFields.model_fields
            }),
        )

    def submit_decision(self, case_id: str, request: DecisionRequest, actor_role: ReviewerRole = ReviewerRole.FRAUD_ANALYST) -> DecisionResponse:
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
        self.audit_service.record_event(
            case_id=case_id,
            event_type=AuditEventType.HUMAN_DECISION_SUBMITTED,
            actor=normalized_request.reviewed_by,
            actor_role=actor_role,
            decision=normalized_request.decision.upper(),
            comment=normalized_request.comment,
        )

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

        self.status_service.set_initial_status(case_id, alert.get("status"))
        return alert

    def get_status(self, case_id: str) -> CaseStatus:
        alert = self.ensure_case_exists(case_id)
        return self.status_service.get_status(case_id, alert.get("status"))

    def set_investigation_result(self, case_id: str, investigation: dict) -> None:
        summary = investigation.get("investigation_summary", {})
        recommendation = summary.get("recommended_action")
        try:
            normalized_recommendation = normalize_decision(recommendation)
        except ValueError:
            normalized_recommendation = None
        self._ai_recommendations[case_id] = normalized_recommendation
        self._investigation_summaries[case_id] = summary

    def get_ai_recommendation(self, case_id: str) -> str | None:
        if case_id in self._ai_recommendations:
            return self._ai_recommendations.get(case_id)
        alert = self.repository.get_alert(case_id)
        if not alert:
            return None
        for recommendation in (
            alert.get("ai_recommendation"),
            (alert.get("investigation_summary") or {}).get("recommended_action")
            if isinstance(alert.get("investigation_summary"), dict)
            else None,
            (alert.get("investigation_result") or {}).get("investigation_summary", {}).get("recommended_action")
            if isinstance(alert.get("investigation_result"), dict)
            else None,
            (alert.get("latest_investigation") or {}).get("recommendation")
            if isinstance(alert.get("latest_investigation"), dict)
            else None,
        ):
            try:
                normalized = normalize_decision(recommendation)
            except ValueError:
                normalized = None
            if normalized:
                return normalized
        return None
