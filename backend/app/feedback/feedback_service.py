from datetime import UTC, datetime
from uuid import uuid4

from app.auth.current_user import AuthenticatedUser
from app.core.constants import AuditEventType, FeedbackDisposition, FeedbackIssueType, FeedbackRating, FeedbackSeverity, NotificationPriority, NotificationRecipientType, ReviewerRole
from app.feedback.feedback_backlog_service import FeedbackBacklogService
from app.feedback.feedback_config import feedback_config
from app.feedback.feedback_repository import FeedbackRepository
from app.feedback.feedback_sanitizer import sanitize_ai_output_snapshot, sanitize_feedback_comment, sanitize_feedback_payload
from app.feedback.feedback_validation_service import FeedbackValidationService
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.repositories.case_repository import CaseRepository
from app.schemas.feedback_schema import FeedbackCreateRequest, FeedbackDispositionUpdateRequest
from app.services.audit_service import audit_service
from app.services.errors import ApiError


class FeedbackService:
    def __init__(
        self,
        repository: FeedbackRepository | None = None,
        backlog_service: FeedbackBacklogService | None = None,
        validation_service: FeedbackValidationService | None = None,
        case_repository: CaseRepository | None = None,
    ) -> None:
        self.repository = repository or FeedbackRepository()
        self.backlog_service = backlog_service or FeedbackBacklogService()
        self.validation_service = validation_service or FeedbackValidationService()
        self.case_repository = case_repository or CaseRepository()

    def submit_feedback(self, request: FeedbackCreateRequest, current_user: AuthenticatedUser) -> dict:
        if not feedback_config.enabled:
            raise ApiError(503, "feedback_loop_disabled", "AI feedback loop is disabled.")
        case = self.case_repository.get_case_by_id(request.case_id)
        if not case:
            raise ApiError(404, "case_not_found", f"Case '{request.case_id}' was not found.")
        self.validation_service.validate_feedback_create(request, case)
        now = datetime.now(UTC).isoformat()
        payload = request.model_dump(mode="json")
        feedback = {
            **payload,
            "feedback_id": f"FB-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "comment": sanitize_feedback_comment(request.comment),
            "suggested_correction": sanitize_feedback_comment(request.suggested_correction),
            "actual_ai_recommendation": request.actual_ai_recommendation or self._case_ai_recommendation(case),
            "human_decision": request.human_decision or self._case_human_decision(case),
            "submitted_by": current_user.user_id,
            "submitted_by_role": current_user.primary_role,
            "disposition": FeedbackDisposition.NEW.value,
            "case_status_at_feedback": case.get("status"),
            "ai_provider": request.ai_provider or "local",
            "model_or_deployment": request.model_or_deployment or "local-deterministic",
            "sanitized_ai_output_snapshot": sanitize_ai_output_snapshot(request.sanitized_ai_output_snapshot),
            "metadata": sanitize_feedback_payload(self.enrich_feedback_with_case_context(payload.get("metadata") or {}, case)),
            "created_at": now,
            "updated_at": now,
        }
        saved = self.repository.append_feedback(feedback)
        self._audit(AuditEventType.AI_FEEDBACK_SUBMITTED, saved, current_user)
        self._track(saved)
        if self._is_critical(saved):
            self._audit(AuditEventType.AI_FEEDBACK_CRITICAL_ISSUE_REPORTED, saved, current_user)
            get_telemetry_client().track_event(telemetry_events.AI_FEEDBACK_CRITICAL_SUBMITTED, self._telemetry_props(saved), {"critical_feedback_count": 1})
            if feedback_config.auto_create_backlog_for_critical:
                self.backlog_service.create_backlog_item_from_feedback(saved)
            if feedback_config.auto_notify_admin_for_critical:
                self._notify_critical_feedback(saved)
        return saved

    def get_feedback(self, feedback_id: str) -> dict:
        feedback = self.repository.get_feedback_by_id(feedback_id)
        if not feedback:
            raise ApiError(404, "feedback_not_found", f"Feedback {feedback_id} was not found.")
        return feedback

    def search_feedback(self, filters: dict) -> dict:
        records = self.repository.search_feedback(**filters)
        return {"count": len(records), "feedback_records": records}

    def get_case_feedback(self, case_id: str) -> dict:
        if not self.case_repository.get_case_by_id(case_id):
            raise ApiError(404, "case_not_found", f"Case '{case_id}' was not found.")
        records = self.repository.search_feedback(case_id=case_id, limit=500)
        return {"count": len(records), "feedback_records": records}

    def update_feedback_disposition(self, feedback_id: str, request: FeedbackDispositionUpdateRequest, current_user: AuthenticatedUser) -> dict:
        self.validation_service.validate_disposition_update(request)
        feedback = self.get_feedback(feedback_id)
        updated = self.repository.update_feedback(feedback_id, {
            "disposition": request.disposition.value,
            "updated_at": datetime.now(UTC).isoformat(),
            "metadata": {
                **feedback.get("metadata", {}),
                "disposition_updated_by": request.updated_by or current_user.user_id,
                "disposition_comment": sanitize_feedback_comment(request.comment),
            },
        })
        self._audit(AuditEventType.AI_FEEDBACK_DISPOSITION_UPDATED, updated, current_user)
        return updated

    def create_feedback_from_human_review(self, case_id: str, review_result: dict, current_user: AuthenticatedUser) -> dict | None:
        if not review_result.get("human_override"):
            return None
        request = FeedbackCreateRequest(
            case_id=case_id,
            target_type="AI_RECOMMENDATION",
            rating=FeedbackRating.POOR,
            issue_types=[FeedbackIssueType.INCORRECT_RECOMMENDATION],
            severity=FeedbackSeverity.HIGH,
            comment=review_result.get("override_reason") or "Human reviewer overrode the AI recommendation.",
            expected_recommendation=review_result.get("human_decision"),
            actual_ai_recommendation=review_result.get("ai_recommendation"),
            human_decision=review_result.get("human_decision"),
            metadata={"source": "human_review"},
        )
        return self.submit_feedback(request, current_user)

    def enrich_feedback_with_case_context(self, feedback: dict, case: dict) -> dict:
        return {
            **feedback,
            "case_severity": case.get("severity"),
            "case_status": case.get("status"),
            "risk_indicator_codes": [item.get("code") for item in case.get("risk_indicators", []) if isinstance(item, dict)],
        }

    def _is_critical(self, feedback: dict) -> bool:
        return feedback.get("severity") == FeedbackSeverity.CRITICAL.value or bool(set(feedback.get("issue_types", [])).intersection(set(feedback_config.critical_issue_types)))

    def _audit(self, event_type: AuditEventType, feedback: dict, current_user: AuthenticatedUser) -> None:
        audit_service.record_event(
            feedback.get("case_id"),
            event_type,
            current_user.user_id,
            ReviewerRole(current_user.primary_role) if current_user.primary_role in ReviewerRole._value2member_map_ else ReviewerRole.UNKNOWN,
            metadata={
                "feedback_id": feedback.get("feedback_id"),
                "case_id": feedback.get("case_id"),
                "target_type": feedback.get("target_type"),
                "rating": feedback.get("rating"),
                "issue_types": feedback.get("issue_types"),
                "severity": feedback.get("severity"),
                "disposition": feedback.get("disposition"),
                "submitted_by": feedback.get("submitted_by"),
                "submitted_by_role": feedback.get("submitted_by_role"),
            },
        )

    def _track(self, feedback: dict) -> None:
        get_telemetry_client().track_event(telemetry_events.AI_FEEDBACK_SUBMITTED, self._telemetry_props(feedback), {"feedback_count": 1})
        if feedback.get("rating") in {FeedbackRating.VERY_POOR.value, FeedbackRating.POOR.value}:
            get_telemetry_client().track_event(telemetry_events.AI_FEEDBACK_NEGATIVE_SUBMITTED, self._telemetry_props(feedback), {"feedback_count": 1})

    @staticmethod
    def _telemetry_props(feedback: dict) -> dict:
        return {
            "target_type": feedback.get("target_type"),
            "rating": feedback.get("rating"),
            "severity": feedback.get("severity"),
            "issue_type_count": len(feedback.get("issue_types", [])),
            "agent_name": feedback.get("agent_name"),
            "ai_provider": feedback.get("ai_provider"),
            "model_or_deployment": feedback.get("model_or_deployment"),
        }

    @staticmethod
    def _case_ai_recommendation(case: dict) -> str | None:
        summary = case.get("investigation_summary") if isinstance(case.get("investigation_summary"), dict) else {}
        return case.get("ai_recommendation") or summary.get("recommended_action")

    @staticmethod
    def _case_human_decision(case: dict) -> str | None:
        review = case.get("human_review") if isinstance(case.get("human_review"), dict) else {}
        return review.get("human_decision") or review.get("decision")

    @staticmethod
    def _notify_critical_feedback(feedback: dict) -> None:
        try:
            from app.notifications.notification_service import notification_service

            notification_service.create_notification(
                event_type="AI_FEEDBACK_CRITICAL_SUBMITTED",
                recipient_type=NotificationRecipientType.ROLE.value,
                recipient_id=None,
                recipient_role="ADMIN",
                title="Critical AI feedback submitted",
                message=f"Critical feedback {feedback.get('feedback_id')} was submitted for case {feedback.get('case_id')}.",
                priority=NotificationPriority.CRITICAL.value,
                case_id=feedback.get("case_id"),
                metadata={"feedback_id": feedback.get("feedback_id"), "severity": feedback.get("severity"), "issue_types": feedback.get("issue_types", [])},
            )
            if FeedbackIssueType.SAFETY_CONCERN.value in feedback.get("issue_types", []) or FeedbackIssueType.PII_CONCERN.value in feedback.get("issue_types", []):
                notification_service.create_notification(
                    event_type="AI_FEEDBACK_CRITICAL_SUBMITTED",
                    recipient_type=NotificationRecipientType.ROLE.value,
                    recipient_id=None,
                    recipient_role="COMPLIANCE_OFFICER",
                    title="Critical AI safety feedback submitted",
                    message=f"Safety-related AI feedback {feedback.get('feedback_id')} needs compliance review.",
                    priority=NotificationPriority.CRITICAL.value,
                    case_id=feedback.get("case_id"),
                    metadata={"feedback_id": feedback.get("feedback_id"), "issue_types": feedback.get("issue_types", [])},
                )
        except Exception:
            return None


feedback_service = FeedbackService()
