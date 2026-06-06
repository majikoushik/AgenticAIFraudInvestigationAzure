from app.core.constants import (
    CaseStatus,
    DECISION_TO_STATUS,
    ReviewerRole,
    normalize_decision,
)
from app.core.permissions import all_reason_codes, allowed_decisions_for_role, assert_decision_allowed
from app.repositories.case_repository import CaseRepository
from app.schemas.review_schema import (
    CloseCaseRequest,
    CloseCaseResponse,
    HumanReviewRequest,
    HumanReviewResponse,
    ReviewOptionsResponse,
)
from app.services.audit_service import AuditService
from app.services.case_service import CaseService
from app.services.case_status_service import CaseStatusService
from app.services.errors import ApiError
from app.services.human_override_service import HumanOverrideService


class HumanReviewService:
    def __init__(
        self,
        repository: CaseRepository,
        audit_service: AuditService,
        status_service: CaseStatusService,
        override_service: HumanOverrideService | None = None,
    ) -> None:
        self.repository = repository
        self.case_service = CaseService(repository, audit_service, status_service)
        self.audit_service = audit_service
        self.status_service = status_service
        self.override_service = override_service or HumanOverrideService(repository)
        self._reviews: dict[str, dict] = {}

    def submit_review(self, case_id: str, request: HumanReviewRequest) -> HumanReviewResponse:
        case_detail = self.case_service.get_case_detail(case_id)
        current_status = CaseStatus(case_detail.current_status)
        if current_status != CaseStatus.PENDING_HUMAN_REVIEW:
            raise ApiError(
                400,
                "case_not_pending_review",
                "Human review can only be submitted when case status is PENDING_HUMAN_REVIEW.",
            )

        assert_decision_allowed(request.reviewer_role, request.decision)
        ai_recommendation = self.get_latest_ai_recommendation(case_detail.model_dump())
        override_record = self.override_service.build_override_record(
            ai_recommendation=ai_recommendation,
            human_decision=request.decision.value,
            reviewed_by=request.reviewed_by,
            override_reason=request.override_reason,
        )

        new_status = DECISION_TO_STATUS[request.decision]
        status_result = self.status_service.transition_case_status(
            case_id,
            new_status.value,
            actor=request.reviewed_by,
            actor_role=request.reviewer_role.value,
            comment=request.comment,
        )
        previous_status = CaseStatus(status_result["previous_status"])
        transitioned_status = CaseStatus(status_result["new_status"])
        human_review = {
            "decision": request.decision.value,
            "human_decision": override_record["human_decision"],
            "reviewed_by": request.reviewed_by,
            "reviewer_role": request.reviewer_role.value,
            "reason_code": request.reason_code.value,
            "comment": request.comment,
            "ai_recommendation": override_record["ai_recommendation"],
            "human_override": override_record["human_override"],
            "override_reason": override_record["override_reason"],
            "override_comparison_status": override_record["override_comparison_status"],
            "override_detected_at": override_record["override_detected_at"],
            "override_detected_by": override_record["override_detected_by"],
        }
        override_summary = self._build_override_summary(override_record)
        self._reviews[case_id] = human_review
        self.repository.update_case_human_review(case_id, human_review)
        self.repository.update_case_override_summary(case_id, override_summary)

        self.audit_service.create_human_decision_event(
            actor=request.reviewed_by,
            actor_role=request.reviewer_role,
            case_id=case_id,
            decision=request.decision.value,
            reason_code=request.reason_code.value,
            comment=request.comment,
            ai_recommendation=override_record["ai_recommendation"],
            human_override=override_record["human_override"],
            metadata={"override_comparison_status": override_record["override_comparison_status"]},
        )
        if override_record["human_override"]:
            self.audit_service.create_human_override_event(
                case_id=case_id,
                actor=request.reviewed_by,
                actor_role=request.reviewer_role,
                ai_recommendation=override_record["ai_recommendation"],
                human_decision=override_record["human_decision"],
                override_reason=override_record["override_reason"],
            )

        return HumanReviewResponse(
            case_id=case_id,
            previous_status=previous_status.value,
            new_status=transitioned_status.value,
            decision=request.decision.value,
            reviewed_by=request.reviewed_by,
            reviewer_role=request.reviewer_role.value,
            reason_code=request.reason_code.value,
            ai_recommendation=override_record["ai_recommendation"],
            human_decision=override_record["human_decision"],
            human_override=override_record["human_override"],
            override_reason=override_record["override_reason"],
            override_comparison_status=override_record["override_comparison_status"],
            override_detected_at=override_record["override_detected_at"],
            override_detected_by=override_record["override_detected_by"],
            message="Human review submitted successfully",
        )

    def close_case(self, case_id: str, request: CloseCaseRequest) -> CloseCaseResponse:
        self.case_service.ensure_case_exists(case_id)
        if request.closer_role not in {ReviewerRole.FRAUD_MANAGER, ReviewerRole.COMPLIANCE_OFFICER}:
            raise ApiError(403, "close_not_allowed", f"Reviewer role {request.closer_role.value} is not allowed to close cases.")

        current_status = self.case_service.get_status(case_id)
        if current_status not in {CaseStatus.APPROVED, CaseStatus.HELD, CaseStatus.ESCALATED, CaseStatus.REJECTED}:
            raise ApiError(400, "case_not_closable", "Case can be closed only after a final human decision.")

        status_result = self.status_service.transition_case_status(
            case_id,
            CaseStatus.CLOSED.value,
            actor=request.closed_by,
            actor_role=request.closer_role.value,
            comment=request.comment,
        )
        return CloseCaseResponse(
            case_id=case_id,
            previous_status=status_result["previous_status"],
            new_status=status_result["new_status"],
            message="Case closed successfully",
        )

    def get_review_options(self, role: ReviewerRole) -> ReviewOptionsResponse:
        return ReviewOptionsResponse(
            reviewer_role=role.value,
            allowed_decisions=allowed_decisions_for_role(role),
            reason_codes=all_reason_codes(),
        )

    def get_override_summary(self, case_id: str) -> dict:
        return self.override_service.get_case_override_summary(case_id)

    def get_latest_ai_recommendation(self, case: dict) -> str | None:
        for recommendation in (
            case.get("ai_recommendation"),
            (case.get("investigation_summary") or {}).get("recommended_action")
            if isinstance(case.get("investigation_summary"), dict)
            else None,
            (case.get("investigation_result") or {}).get("investigation_summary", {}).get("recommended_action")
            if isinstance(case.get("investigation_result"), dict)
            else None,
            (case.get("latest_investigation") or {}).get("recommendation")
            if isinstance(case.get("latest_investigation"), dict)
            else None,
        ):
            try:
                normalized = normalize_decision(recommendation)
            except ValueError:
                normalized = None
            if normalized:
                return normalized
        return None

    @staticmethod
    def _build_override_summary(override_record: dict) -> dict:
        return {
            "has_override": override_record["human_override"],
            "ai_recommendation": override_record["ai_recommendation"],
            "human_decision": override_record["human_decision"],
            "override_reason": override_record["override_reason"],
            "override_detected_at": override_record["override_detected_at"],
            "override_detected_by": override_record["override_detected_by"],
            "override_comparison_status": override_record["override_comparison_status"],
        }
