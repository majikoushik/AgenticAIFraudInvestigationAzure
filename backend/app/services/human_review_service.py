from app.core.constants import (
    AuditEventType,
    CaseStatus,
    DECISION_TO_STATUS,
    ReviewDecision,
    ReviewerRole,
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


class HumanReviewService:
    def __init__(
        self,
        repository: CaseRepository,
        audit_service: AuditService,
        status_service: CaseStatusService,
    ) -> None:
        self.case_service = CaseService(repository, audit_service, status_service)
        self.audit_service = audit_service
        self.status_service = status_service
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
        ai_recommendation = self.case_service.get_ai_recommendation(case_id)
        human_override = bool(ai_recommendation and ai_recommendation != request.decision.value)
        if human_override and not request.override_reason:
            raise ApiError(
                400,
                "override_reason_required",
                "Override reason is required when human decision differs from AI recommendation.",
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
        self._reviews[case_id] = {
            "decision": request.decision.value,
            "reviewed_by": request.reviewed_by,
            "reviewer_role": request.reviewer_role.value,
            "reason_code": request.reason_code.value,
            "human_override": human_override,
            "override_reason": request.override_reason,
        }

        self.audit_service.create_human_decision_event(
            actor=request.reviewed_by,
            actor_role=request.reviewer_role,
            case_id=case_id,
            decision=request.decision.value,
            reason_code=request.reason_code.value,
            comment=request.comment,
            ai_recommendation=ai_recommendation,
            human_override=human_override,
        )
        if human_override:
            self.audit_service.create_human_override_event(
                case_id=case_id,
                actor=request.reviewed_by,
                actor_role=request.reviewer_role,
                ai_recommendation=ai_recommendation,
                human_decision=request.decision.value,
                override_reason=request.override_reason,
            )

        return HumanReviewResponse(
            case_id=case_id,
            previous_status=previous_status.value,
            new_status=transitioned_status.value,
            decision=request.decision.value,
            reviewed_by=request.reviewed_by,
            reviewer_role=request.reviewer_role.value,
            reason_code=request.reason_code.value,
            ai_recommendation=ai_recommendation,
            human_override=human_override,
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
