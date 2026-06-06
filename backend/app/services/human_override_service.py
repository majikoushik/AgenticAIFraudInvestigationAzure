from datetime import UTC, datetime
from typing import Any

from app.core.constants import OverrideComparisonStatus, normalize_decision
from app.repositories.case_repository import CaseRepository
from app.services.errors import ApiError


class HumanOverrideService:
    def __init__(self, repository: CaseRepository | None = None) -> None:
        self.repository = repository or CaseRepository()

    def compare_decisions(self, ai_recommendation: str | None, human_decision: str) -> dict[str, Any]:
        if not human_decision or not human_decision.strip():
            raise ApiError(400, "decision_required", "Human decision is required.")

        try:
            normalized_human_decision = normalize_decision(human_decision)
            normalized_ai_recommendation = normalize_decision(ai_recommendation)
        except ValueError as exc:
            raise ApiError(400, "invalid_decision", "Decision must be one of: APPROVE, HOLD, ESCALATE, REJECT.") from exc

        if normalized_human_decision is None:
            raise ApiError(400, "decision_required", "Human decision is required.")

        if normalized_ai_recommendation is None:
            return {
                "ai_recommendation": None,
                "human_decision": normalized_human_decision,
                "human_override": False,
                "override_comparison_status": OverrideComparisonStatus.AI_RECOMMENDATION_MISSING.value,
            }

        human_override = normalized_ai_recommendation != normalized_human_decision
        return {
            "ai_recommendation": normalized_ai_recommendation,
            "human_decision": normalized_human_decision,
            "human_override": human_override,
            "override_comparison_status": (
                OverrideComparisonStatus.OVERRIDDEN.value
                if human_override
                else OverrideComparisonStatus.MATCHED.value
            ),
        }

    def validate_override_reason(self, human_override: bool, override_reason: str | None) -> None:
        if not human_override:
            return

        if not override_reason or not override_reason.strip():
            raise ApiError(
                400,
                "override_reason_required",
                "Override reason is required when human decision differs from AI recommendation.",
            )
        if len(override_reason.strip()) < 10:
            raise ApiError(
                400,
                "override_reason_too_short",
                "Override reason must be at least 10 characters.",
            )

    def build_override_record(
        self,
        ai_recommendation: str | None,
        human_decision: str,
        reviewed_by: str,
        override_reason: str | None,
    ) -> dict[str, Any]:
        comparison = self.compare_decisions(ai_recommendation, human_decision)
        self.validate_override_reason(comparison["human_override"], override_reason)

        override_detected_at = datetime.now(UTC).isoformat() if comparison["human_override"] else None
        return {
            **comparison,
            "override_reason": override_reason.strip() if comparison["human_override"] and override_reason else None,
            "override_detected_at": override_detected_at,
            "override_detected_by": reviewed_by if comparison["human_override"] else None,
        }

    def get_case_override_summary(self, case_id: str) -> dict[str, Any]:
        case = self.repository.get_case_by_id(case_id)
        if case is None:
            raise ApiError(404, "case_not_found", f"Case '{case_id}' was not found.")

        summary = case.get("override_summary")
        if isinstance(summary, dict):
            return {"case_id": case_id, **summary}

        human_review = case.get("human_review") if isinstance(case.get("human_review"), dict) else {}
        if not human_review:
            try:
                ai_recommendation = normalize_decision(case.get("ai_recommendation"))
            except ValueError:
                ai_recommendation = None
            return {
                "case_id": case_id,
                "has_override": False,
                "ai_recommendation": ai_recommendation,
                "human_decision": None,
                "override_reason": None,
                "override_detected_at": None,
                "override_detected_by": None,
                "override_comparison_status": OverrideComparisonStatus.NOT_APPLICABLE.value,
            }

        comparison = self.compare_decisions(
            case.get("ai_recommendation"),
            human_review.get("human_decision") or human_review.get("decision"),
        )
        return {
            "case_id": case_id,
            "has_override": False,
            "ai_recommendation": comparison["ai_recommendation"],
            "human_decision": human_review.get("human_decision") or comparison["human_decision"],
            "override_reason": None,
            "override_detected_at": None,
            "override_detected_by": None,
            "override_comparison_status": comparison["override_comparison_status"],
        }


human_override_service = HumanOverrideService()
