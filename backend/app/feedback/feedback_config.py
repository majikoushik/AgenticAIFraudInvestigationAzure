from dataclasses import dataclass

from app.config import settings


def _csv(value: str) -> list[str]:
    return [item.strip().upper() for item in (value or "").split(",") if item.strip()]


@dataclass(frozen=True)
class FeedbackConfig:
    enabled: bool = settings.feedback_loop_enabled
    mode: str = settings.feedback_mode
    feedback_local_store_path: str = settings.feedback_local_store_path
    feedback_backlog_store_path: str = settings.feedback_backlog_store_path
    feedback_export_path: str = settings.feedback_export_path
    allow_case_level_feedback: bool = settings.feedback_allow_case_level_feedback
    allow_agent_level_feedback: bool = settings.feedback_allow_agent_level_feedback
    allow_citation_level_feedback: bool = settings.feedback_allow_citation_level_feedback
    allow_anonymous_feedback: bool = settings.feedback_allow_anonymous_feedback
    require_comment_for_negative_rating: bool = settings.feedback_require_comment_for_negative_rating
    negative_ratings: list[str] = None
    min_comment_length: int = settings.feedback_min_comment_length
    critical_issue_types: list[str] = None
    auto_create_backlog_for_critical: bool = settings.feedback_auto_create_backlog_for_critical
    auto_notify_admin_for_critical: bool = settings.feedback_auto_notify_admin_for_critical
    auto_export_accepted_to_eval: bool = settings.feedback_auto_export_accepted_to_eval

    def __post_init__(self) -> None:
        object.__setattr__(self, "negative_ratings", _csv(settings.feedback_negative_ratings))
        object.__setattr__(self, "critical_issue_types", _csv(settings.feedback_critical_issue_types))

    def safe_summary(self) -> dict:
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "allow_case_level_feedback": self.allow_case_level_feedback,
            "allow_agent_level_feedback": self.allow_agent_level_feedback,
            "allow_citation_level_feedback": self.allow_citation_level_feedback,
            "allow_anonymous_feedback": self.allow_anonymous_feedback,
            "require_comment_for_negative_rating": self.require_comment_for_negative_rating,
            "negative_ratings": self.negative_ratings,
            "min_comment_length": self.min_comment_length,
            "critical_issue_types": self.critical_issue_types,
            "auto_create_backlog_for_critical": self.auto_create_backlog_for_critical,
            "auto_notify_admin_for_critical": self.auto_notify_admin_for_critical,
            "auto_export_accepted_to_eval": self.auto_export_accepted_to_eval,
        }


feedback_config = FeedbackConfig()
