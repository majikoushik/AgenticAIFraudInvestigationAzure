from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.constants import FeedbackIssueType, FeedbackRating, FeedbackSeverity, FeedbackTargetType
from app.feedback.feedback_backlog_service import FeedbackBacklogService
from app.feedback.feedback_repository import FeedbackRepository
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client


class FeedbackAnalyticsService:
    def __init__(self, repository: FeedbackRepository | None = None, backlog_service: FeedbackBacklogService | None = None) -> None:
        self.repository = repository or FeedbackRepository()
        self.backlog_service = backlog_service or FeedbackBacklogService()

    def get_feedback_summary(self) -> dict[str, Any]:
        records = self.repository.list_feedback()
        negative = [item for item in records if item.get("rating") in {FeedbackRating.VERY_POOR.value, FeedbackRating.POOR.value}]
        positive = [item for item in records if item.get("rating") in {FeedbackRating.GOOD.value, FeedbackRating.EXCELLENT.value}]
        critical = [item for item in records if item.get("severity") == FeedbackSeverity.CRITICAL.value]
        open_backlog = [item for item in self.backlog_service.list_backlog_items() if item.get("status") not in {"RESOLVED", "CLOSED"}]
        total = len(records)
        summary = {
            "total_feedback": total,
            "positive_feedback_count": len(positive),
            "negative_feedback_count": len(negative),
            "neutral_feedback_count": total - len(positive) - len(negative),
            "negative_feedback_rate_percentage": round((len(negative) / total) * 100, 2) if total else 0.0,
            "critical_feedback_count": len(critical),
            "open_backlog_count": len(open_backlog),
        }
        get_telemetry_client().track_event(telemetry_events.AI_FEEDBACK_ANALYTICS_CALCULATED, {}, {"feedback_count": total, "negative_feedback_rate": summary["negative_feedback_rate_percentage"], "critical_feedback_count": len(critical), "backlog_count": len(open_backlog)})
        return summary

    def get_feedback_by_rating(self) -> dict[str, int]:
        return self._count("rating", [item.value for item in FeedbackRating])

    def get_feedback_by_issue_type(self) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for item in self.repository.list_feedback():
            counter.update(item.get("issue_types", []))
        return {key: counter.get(key, 0) for key in [item.value for item in FeedbackIssueType]}

    def get_feedback_by_target_type(self) -> dict[str, int]:
        return self._count("target_type", [item.value for item in FeedbackTargetType])

    def get_feedback_by_agent(self) -> dict[str, int]:
        return self._count_dynamic("agent_name")

    def get_feedback_by_ai_provider(self) -> dict[str, int]:
        return self._count_dynamic("ai_provider")

    def get_negative_feedback_rate(self) -> dict[str, Any]:
        summary = self.get_feedback_summary()
        return {"negative_feedback_rate_percentage": summary["negative_feedback_rate_percentage"], "negative_feedback_count": summary["negative_feedback_count"], "total_feedback": summary["total_feedback"]}

    def get_critical_feedback_count(self) -> dict[str, int]:
        return {"critical_feedback_count": self.get_feedback_summary()["critical_feedback_count"]}

    def get_feedback_trends(self, days: int = 30) -> dict[str, Any]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        by_day: defaultdict[str, int] = defaultdict(int)
        negative_by_day: defaultdict[str, int] = defaultdict(int)
        critical_by_day: defaultdict[str, int] = defaultdict(int)
        for item in self.repository.list_feedback():
            created = str(item.get("created_at", ""))
            day = created[:10]
            if not day:
                continue
            try:
                if datetime.fromisoformat(created.replace("Z", "+00:00")) < cutoff:
                    continue
            except ValueError:
                pass
            by_day[day] += 1
            if item.get("rating") in {FeedbackRating.VERY_POOR.value, FeedbackRating.POOR.value}:
                negative_by_day[day] += 1
            if item.get("severity") == FeedbackSeverity.CRITICAL.value:
                critical_by_day[day] += 1
        return {"feedback_by_day": dict(by_day), "negative_feedback_by_day": dict(negative_by_day), "critical_feedback_by_day": dict(critical_by_day)}

    def get_recommendation_quality_metrics(self) -> dict[str, Any]:
        records = self.repository.list_feedback()
        actual = Counter(item.get("actual_ai_recommendation") or "UNKNOWN" for item in records if item.get("target_type") == FeedbackTargetType.AI_RECOMMENDATION.value)
        expected = Counter(item.get("expected_recommendation") or "UNKNOWN" for item in records if item.get("target_type") == FeedbackTargetType.AI_RECOMMENDATION.value)
        incorrect = [item for item in records if FeedbackIssueType.INCORRECT_RECOMMENDATION.value in item.get("issue_types", [])]
        return {
            "incorrect_recommendation_count": len(incorrect),
            "recommendation_feedback_rate": len(actual),
            "feedback_count_by_actual_ai_recommendation": dict(actual),
            "feedback_count_by_expected_recommendation": dict(expected),
        }

    def get_rag_quality_feedback_metrics(self) -> dict[str, Any]:
        issue_counts = self.get_feedback_by_issue_type()
        citation_records = [item for item in self.repository.list_feedback() if item.get("target_type") in {FeedbackTargetType.POLICY_CITATION.value, FeedbackTargetType.SIMILAR_CASE_RETRIEVAL.value}]
        return {
            "wrong_policy_citation_count": issue_counts.get(FeedbackIssueType.WRONG_POLICY_CITATION.value, 0),
            "missing_policy_citation_count": issue_counts.get(FeedbackIssueType.MISSING_POLICY_CITATION.value, 0),
            "irrelevant_similar_case_count": issue_counts.get(FeedbackIssueType.IRRELEVANT_SIMILAR_CASE.value, 0),
            "missing_similar_case_count": issue_counts.get(FeedbackIssueType.MISSING_SIMILAR_CASE.value, 0),
            "citation_feedback_rate": len(citation_records),
        }

    def get_prompt_improvement_backlog_metrics(self) -> dict[str, Any]:
        items = self.backlog_service.list_backlog_items()
        return {"open_prompt_backlog_count": len([item for item in items if item.get("backlog_type") == "PROMPT_IMPROVEMENT" and item.get("status") == "OPEN"]), "open_backlog_count": len([item for item in items if item.get("status") == "OPEN"])}

    def get_all_metrics(self) -> dict[str, Any]:
        return {
            "summary": self.get_feedback_summary(),
            "by_rating": self.get_feedback_by_rating(),
            "by_issue_type": self.get_feedback_by_issue_type(),
            "by_target_type": self.get_feedback_by_target_type(),
            "by_agent": self.get_feedback_by_agent(),
            "by_ai_provider": self.get_feedback_by_ai_provider(),
            "recommendation_quality": self.get_recommendation_quality_metrics(),
            "rag_quality": self.get_rag_quality_feedback_metrics(),
            "trends": self.get_feedback_trends(),
            "backlog": self.get_prompt_improvement_backlog_metrics(),
        }

    def _count(self, field: str, known: list[str]) -> dict[str, int]:
        counter = Counter(item.get(field) for item in self.repository.list_feedback())
        return {key: counter.get(key, 0) for key in known}

    def _count_dynamic(self, field: str) -> dict[str, int]:
        return dict(Counter(item.get(field) or "UNKNOWN" for item in self.repository.list_feedback()))
