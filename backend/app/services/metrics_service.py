from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean
from typing import Any

from app.core.constants import AuditEventType, CaseStatus, normalize_decision
from app.feedback.feedback_analytics_service import FeedbackAnalyticsService
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.repositories.audit_repository import AuditRepository
from app.repositories.case_repository import CaseRepository
from app.schemas.metrics_schema import (
    AIRecommendationMetrics,
    AgentExecutionMetrics,
    AiVsHumanMetricsResponse,
    AuditMetrics,
    CaseStatusMetrics,
    HumanDecisionMetrics,
    HumanOverrideMetrics,
    HumanReviewTimeMetrics,
    InvestigationTimeMetrics,
    MetricsSummaryResponse,
    OperationsMetricsResponse,
    PolicyCitationMetrics,
    RagRetrievalMetrics,
)


DECISION_KEYS = ["APPROVE", "HOLD", "ESCALATE", "REJECT"]
STATUS_KEYS = [status.value for status in CaseStatus]


class MetricsService:
    def __init__(
        self,
        case_repository: CaseRepository | None = None,
        audit_repository: AuditRepository | None = None,
    ) -> None:
        self.case_repository = case_repository or CaseRepository()
        self.audit_repository = audit_repository or AuditRepository()
        self.feedback_analytics_service = FeedbackAnalyticsService()

    def get_summary_metrics(self) -> MetricsSummaryResponse:
        summary = MetricsSummaryResponse(
            case_status_metrics=self.get_case_status_metrics(),
            ai_recommendation_metrics=self.get_ai_recommendation_metrics(),
            human_decision_metrics=self.get_human_decision_metrics(),
            human_override_metrics=self.get_human_override_metrics(),
            investigation_time_metrics=self.get_investigation_time_metrics(),
            human_review_time_metrics=self.get_human_review_time_metrics(),
            agent_execution_metrics=self.get_agent_execution_metrics(),
            rag_retrieval_metrics=self.get_rag_retrieval_metrics(),
            policy_citation_metrics=self.get_policy_citation_metrics(),
            audit_metrics=self.get_audit_metrics(),
        )
        self._emit_business_metrics(summary)
        return summary

    def get_case_status_metrics(self) -> CaseStatusMetrics:
        cases = self._cases()
        counts = Counter(self._normalize_status(case.get("status")) for case in cases)
        total = len(cases)
        status_counts = {status: counts.get(status, 0) for status in STATUS_KEYS}
        return CaseStatusMetrics(
            total_cases=total,
            new_cases=status_counts["NEW"],
            ai_investigation_in_progress_cases=status_counts["AI_INVESTIGATION_IN_PROGRESS"],
            ai_investigation_completed_cases=status_counts["AI_INVESTIGATION_COMPLETED"],
            pending_human_review_cases=status_counts["PENDING_HUMAN_REVIEW"],
            approved_cases=status_counts["APPROVED"],
            held_cases=status_counts["HELD"],
            escalated_cases=status_counts["ESCALATED"],
            rejected_cases=status_counts["REJECTED"],
            closed_cases=status_counts["CLOSED"],
            status_counts=status_counts,
            status_percentages={status: self.safe_percentage(count, total) for status, count in status_counts.items()},
        )

    def get_ai_recommendation_metrics(self) -> AIRecommendationMetrics:
        recommendations = [self._get_ai_recommendation(case) for case in self._cases()]
        counts = self._decision_counts(value for value in recommendations if value)
        total = sum(counts.values())
        return AIRecommendationMetrics(
            total_ai_recommendations=total,
            recommendation_counts=counts,
            recommendation_percentages={key: self.safe_percentage(value, total) for key, value in counts.items()},
            cases_missing_ai_recommendation=sum(1 for value in recommendations if value is None),
        )

    def get_human_decision_metrics(self) -> HumanDecisionMetrics:
        events_by_case = self._latest_events_by_case(AuditEventType.HUMAN_DECISION_SUBMITTED.value)
        decisions = [self._get_human_decision(case, events_by_case.get(case.get("case_id"))) for case in self._cases()]
        counts = self._decision_counts(value for value in decisions if value)
        total = sum(counts.values())
        return HumanDecisionMetrics(
            total_human_decisions=total,
            decision_counts=counts,
            decision_percentages={key: self.safe_percentage(value, total) for key, value in counts.items()},
            cases_without_human_decision=sum(1 for value in decisions if value is None),
        )

    def get_human_override_metrics(self) -> HumanOverrideMetrics:
        overrides = []
        matches = 0
        reviewed = 0
        seen_cases: set[str] = set()

        for case in self._cases():
            case_id = case.get("case_id")
            record = self._get_override_record(case)
            if not record:
                continue
            reviewed += 1
            seen_cases.add(case_id)
            if record.get("human_override"):
                overrides.append(record)
            elif record.get("ai_recommendation") and record.get("human_decision") == record.get("ai_recommendation"):
                matches += 1

        # Audit events are included as a fallback for cases whose JSON record is missing override details.
        for event in self._events():
            if event.get("event_type") != AuditEventType.HUMAN_OVERRIDE_DETECTED.value or event.get("case_id") in seen_cases:
                continue
            reviewed += 1
            overrides.append(
                {
                    "ai_recommendation": self.normalize_decision(event.get("ai_recommendation")),
                    "human_decision": self.normalize_decision(event.get("human_decision")),
                    "human_override": True,
                }
            )

        pair_counts = Counter(
            (record.get("ai_recommendation") or "UNKNOWN", record.get("human_decision") or "UNKNOWN")
            for record in overrides
        )
        return HumanOverrideMetrics(
            total_reviewed_cases=reviewed,
            total_overrides=len(overrides),
            override_rate_percentage=self.safe_percentage(len(overrides), reviewed),
            ai_human_match_count=matches,
            ai_human_match_rate_percentage=self.safe_percentage(matches, reviewed),
            override_counts_by_ai_recommendation=dict(Counter(record.get("ai_recommendation") or "UNKNOWN" for record in overrides)),
            override_counts_by_human_decision=dict(Counter(record.get("human_decision") or "UNKNOWN" for record in overrides)),
            override_pairs=[
                {"ai_recommendation": ai, "human_decision": human, "count": count}
                for (ai, human), count in sorted(pair_counts.items())
            ],
        )

    def get_investigation_time_metrics(self) -> InvestigationTimeMetrics:
        durations, missing = self._paired_durations(
            AuditEventType.AI_INVESTIGATION_STARTED.value,
            AuditEventType.AI_INVESTIGATION_COMPLETED.value,
        )
        return InvestigationTimeMetrics(
            average_ai_investigation_duration_seconds=self._average(durations),
            minimum_ai_investigation_duration_seconds=min(durations) if durations else 0.0,
            maximum_ai_investigation_duration_seconds=max(durations) if durations else 0.0,
            cases_with_missing_investigation_duration=missing,
        )

    def get_human_review_time_metrics(self) -> HumanReviewTimeMetrics:
        start_events = {
            AuditEventType.PENDING_HUMAN_REVIEW_SET.value,
            AuditEventType.CASE_STATUS_CHANGED.value,
        }
        by_case: dict[str, dict[str, datetime]] = defaultdict(dict)
        for event in self._events():
            case_id = event.get("case_id")
            timestamp = self.parse_timestamp(event.get("timestamp"))
            if not case_id or timestamp is None:
                continue
            if event.get("event_type") in start_events and (
                event.get("new_status") == CaseStatus.PENDING_HUMAN_REVIEW.value
                or event.get("event_type") == AuditEventType.PENDING_HUMAN_REVIEW_SET.value
            ):
                by_case[case_id]["start"] = timestamp
            if event.get("event_type") == AuditEventType.HUMAN_DECISION_SUBMITTED.value:
                by_case[case_id]["end"] = timestamp

        durations = [self.calculate_duration_seconds(pair.get("start"), pair.get("end")) for pair in by_case.values()]
        valid = [duration for duration in durations if duration is not None]
        return HumanReviewTimeMetrics(
            average_human_review_wait_time_seconds=self._average(valid),
            minimum_human_review_wait_time_seconds=min(valid) if valid else 0.0,
            maximum_human_review_wait_time_seconds=max(valid) if valid else 0.0,
            cases_with_missing_review_duration=sum(1 for duration in durations if duration is None),
        )

    def get_agent_execution_metrics(self) -> AgentExecutionMetrics:
        events = self._events()
        completed = [event for event in events if event.get("event_type") == AuditEventType.AGENT_EXECUTION_COMPLETED.value]
        failed = [event for event in events if event.get("event_type") == AuditEventType.AGENT_EXECUTION_FAILED.value]
        duration_by_agent: dict[str, list[float]] = defaultdict(list)
        for event in completed:
            agent = event.get("agent_name") or "UNKNOWN"
            duration = self._metadata_number(event, "duration_ms")
            if duration is not None:
                duration_by_agent[agent].append(duration)
        return AgentExecutionMetrics(
            total_agent_executions=len(completed) + len(failed),
            agent_success_count=len(completed),
            agent_failure_count=len(failed),
            agent_failure_rate_percentage=self.safe_percentage(len(failed), len(completed) + len(failed)),
            execution_count_by_agent=dict(Counter(event.get("agent_name") or "UNKNOWN" for event in completed + failed)),
            failure_count_by_agent=dict(Counter(event.get("agent_name") or "UNKNOWN" for event in failed)),
            average_duration_by_agent={agent: round(mean(values), 2) for agent, values in duration_by_agent.items()},
        )

    def get_rag_retrieval_metrics(self) -> RagRetrievalMetrics:
        completed = [event for event in self._events() if event.get("event_type") == AuditEventType.RAG_RETRIEVAL_COMPLETED.value]
        failed = [event for event in self._events() if event.get("event_type") == AuditEventType.RAG_RETRIEVAL_FAILED.value]
        result_counts = [value for value in (self._metadata_number(event, "result_count") for event in completed) if value is not None]
        sources = Counter(source for event in completed for source in event.get("rag_sources", []))
        modes = Counter((event.get("metadata") or {}).get("retrieval_mode", "unknown") for event in completed)
        return RagRetrievalMetrics(
            total_rag_retrievals=len(completed) + len(failed),
            rag_success_count=len(completed),
            rag_failure_count=len(failed),
            rag_failure_rate_percentage=self.safe_percentage(len(failed), len(completed) + len(failed)),
            retrieval_count_by_mode=dict(modes),
            average_result_count=round(mean(result_counts), 2) if result_counts else 0.0,
            top_retrieved_sources=self._top_items(sources),
        )

    def get_policy_citation_metrics(self) -> PolicyCitationMetrics:
        policy_by_case: dict[str, set[str]] = defaultdict(set)
        for case in self._cases():
            for source in self._extract_policy_sources(case):
                policy_by_case[case.get("case_id")].add(source)
        for event in self._events():
            if event.get("event_type") == AuditEventType.RAG_RETRIEVAL_COMPLETED.value:
                for source in event.get("rag_sources", []):
                    policy_by_case[event.get("case_id")].add(source)
        cases_with = sum(1 for case in self._cases() if policy_by_case.get(case.get("case_id")))
        total = len(self._cases())
        source_counts = Counter(source for sources in policy_by_case.values() for source in sources)
        return PolicyCitationMetrics(
            cases_with_policy_references=cases_with,
            cases_without_policy_references=max(total - cases_with, 0),
            policy_reference_rate_percentage=self.safe_percentage(cases_with, total),
            top_policy_sources=self._top_items(source_counts),
        )

    def get_audit_metrics(self) -> AuditMetrics:
        events = self._events()
        latest = max((event.get("timestamp") for event in events if event.get("timestamp")), default=None)
        return AuditMetrics(
            total_audit_events=len(events),
            audit_events_by_category=dict(Counter(event.get("event_category") or "UNKNOWN" for event in events)),
            audit_events_by_type=dict(Counter(event.get("event_type") or "UNKNOWN" for event in events)),
            audit_events_by_actor_role=dict(Counter(event.get("actor_role") or "UNKNOWN" for event in events)),
            latest_audit_event_timestamp=latest,
        )

    def get_ai_vs_human_metrics(self) -> AiVsHumanMetricsResponse:
        override_metrics = self.get_human_override_metrics()
        return AiVsHumanMetricsResponse(
            ai_recommendation_metrics=self.get_ai_recommendation_metrics(),
            human_decision_metrics=self.get_human_decision_metrics(),
            human_override_metrics=override_metrics,
            override_pairs=override_metrics.override_pairs,
        )

    def get_operations_metrics(self) -> OperationsMetricsResponse:
        return OperationsMetricsResponse(
            investigation_time_metrics=self.get_investigation_time_metrics(),
            human_review_time_metrics=self.get_human_review_time_metrics(),
            agent_execution_metrics=self.get_agent_execution_metrics(),
            rag_retrieval_metrics=self.get_rag_retrieval_metrics(),
        )

    def get_timeseries_metrics(self) -> dict:
        cases_created = Counter(self._date_key(case.get("created_at")) for case in self._cases())
        human_decisions = Counter()
        overrides = Counter()
        audit_events = Counter()
        for event in self._events():
            date_key = self._date_key(event.get("timestamp"))
            audit_events[date_key] += 1
            if event.get("event_type") == AuditEventType.HUMAN_DECISION_SUBMITTED.value:
                human_decisions[date_key] += 1
            if event.get("event_type") == AuditEventType.HUMAN_OVERRIDE_DETECTED.value:
                overrides[date_key] += 1
        return {
            "cases_created_by_date": self._clean_date_counts(cases_created),
            "human_decisions_by_date": self._clean_date_counts(human_decisions),
            "overrides_by_date": self._clean_date_counts(overrides),
            "audit_events_by_date": self._clean_date_counts(audit_events),
        }

    def get_feedback_metrics(self) -> dict:
        metrics = self.feedback_analytics_service.get_all_metrics()
        return {
            "total_feedback": metrics["summary"]["total_feedback"],
            "negative_feedback_rate_percentage": metrics["summary"]["negative_feedback_rate_percentage"],
            "critical_feedback_count": metrics["summary"]["critical_feedback_count"],
            "feedback_by_target_type": metrics["by_target_type"],
            "feedback_by_issue_type": metrics["by_issue_type"],
            "feedback_by_agent": metrics["by_agent"],
            "wrong_policy_citation_feedback_count": metrics["rag_quality"]["wrong_policy_citation_count"],
            "incorrect_recommendation_feedback_count": metrics["recommendation_quality"]["incorrect_recommendation_count"],
            "open_feedback_backlog_count": metrics["summary"]["open_backlog_count"],
        }

    @staticmethod
    def normalize_decision(value: str | None) -> str | None:
        try:
            return normalize_decision(value)
        except ValueError:
            return None

    @staticmethod
    def safe_percentage(numerator: int | float, denominator: int | float) -> float:
        return round((numerator / denominator) * 100, 1) if denominator else 0.0

    @staticmethod
    def parse_timestamp(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def calculate_duration_seconds(start: datetime | None, end: datetime | None) -> float | None:
        if not start or not end or end < start:
            return None
        return round((end - start).total_seconds(), 2)

    @staticmethod
    def group_counts(values: list[str]) -> dict[str, int]:
        return dict(Counter(values))

    def get_latest_event_for_case(self, case_id: str, event_type: str) -> dict | None:
        return self._latest_events_by_case(event_type).get(case_id)

    def _cases(self) -> list[dict[str, Any]]:
        return self.case_repository.list_alerts()

    def _events(self) -> list[dict[str, Any]]:
        return self.audit_repository.list_all_events()

    def _decision_counts(self, values) -> dict[str, int]:
        counts = Counter(values)
        return {key: counts.get(key, 0) for key in DECISION_KEYS}

    def _get_ai_recommendation(self, case: dict) -> str | None:
        for value in (
            case.get("ai_recommendation"),
            (case.get("investigation_summary") or {}).get("recommended_action") if isinstance(case.get("investigation_summary"), dict) else None,
            (case.get("investigation_result") or {}).get("investigation_summary", {}).get("recommended_action") if isinstance(case.get("investigation_result"), dict) else None,
            (case.get("latest_investigation") or {}).get("recommendation") if isinstance(case.get("latest_investigation"), dict) else None,
        ):
            decision = self.normalize_decision(value)
            if decision:
                return decision
        return None

    def _get_human_decision(self, case: dict, latest_event: dict | None) -> str | None:
        review = case.get("human_review") if isinstance(case.get("human_review"), dict) else {}
        for value in (
            review.get("human_decision"),
            review.get("decision"),
            case.get("decision"),
            latest_event.get("human_decision") if latest_event else None,
            latest_event.get("decision") if latest_event else None,
        ):
            decision = self.normalize_decision(value)
            if decision:
                return decision
        return None

    def _get_override_record(self, case: dict) -> dict | None:
        summary = case.get("override_summary") if isinstance(case.get("override_summary"), dict) else None
        review = case.get("human_review") if isinstance(case.get("human_review"), dict) else None
        record = summary or review
        if not record:
            return None
        ai = self.normalize_decision(record.get("ai_recommendation") or self._get_ai_recommendation(case))
        human = self.normalize_decision(record.get("human_decision") or record.get("decision"))
        if not human:
            return None
        return {
            "ai_recommendation": ai,
            "human_decision": human,
            "human_override": bool(record.get("human_override") or record.get("has_override")),
        }

    def _paired_durations(self, start_type: str, end_type: str) -> tuple[list[float], int]:
        by_case: dict[str, dict[str, datetime]] = defaultdict(dict)
        for event in self._events():
            case_id = event.get("case_id")
            timestamp = self.parse_timestamp(event.get("timestamp"))
            if not case_id or timestamp is None:
                continue
            if event.get("event_type") == start_type:
                by_case[case_id]["start"] = timestamp
            if event.get("event_type") == end_type:
                by_case[case_id]["end"] = timestamp
        durations = [self.calculate_duration_seconds(pair.get("start"), pair.get("end")) for pair in by_case.values()]
        return [duration for duration in durations if duration is not None], sum(1 for duration in durations if duration is None)

    def _latest_events_by_case(self, event_type: str) -> dict[str, dict]:
        latest: dict[str, dict] = {}
        for event in self._events():
            if event.get("event_type") == event_type and event.get("case_id"):
                latest[event["case_id"]] = event
        return latest

    @staticmethod
    def _normalize_status(value: str | None) -> str:
        try:
            return CaseStatus((value or "NEW").upper()).value
        except ValueError:
            return CaseStatus.NEW.value

    @staticmethod
    def _metadata_number(event: dict, key: str) -> float | None:
        value = (event.get("metadata") or {}).get(key)
        return float(value) if isinstance(value, int | float) else None

    @staticmethod
    def _average(values: list[float]) -> float:
        return round(mean(values), 2) if values else 0.0

    @staticmethod
    def _top_items(counter: Counter) -> list[dict]:
        return [{"name": name, "count": count} for name, count in counter.most_common(10)]

    def _extract_policy_sources(self, case: dict) -> list[str]:
        references = []
        for value in (
            case.get("policy_references"),
            (case.get("investigation_result") or {}).get("policy_references") if isinstance(case.get("investigation_result"), dict) else None,
            (case.get("latest_investigation") or {}).get("policy_references") if isinstance(case.get("latest_investigation"), dict) else None,
        ):
            if isinstance(value, list):
                references.extend(self._source_from_reference(item) for item in value)
        return [source for source in references if source]

    @staticmethod
    def _source_from_reference(reference: Any) -> str | None:
        if isinstance(reference, str):
            return reference
        if isinstance(reference, dict):
            return reference.get("source") or reference.get("source_filename") or reference.get("filename") or reference.get("title")
        return None

    def _date_key(self, value: str | None) -> str | None:
        timestamp = self.parse_timestamp(value)
        return timestamp.date().isoformat() if timestamp else None

    @staticmethod
    def _clean_date_counts(counter: Counter) -> dict[str, int]:
        return {key: value for key, value in sorted(counter.items()) if key}

    @staticmethod
    def _emit_business_metrics(summary: MetricsSummaryResponse) -> None:
        try:
            get_telemetry_client().track_event(
                telemetry_events.BUSINESS_METRICS_CALCULATED,
                {
                    "total_cases": summary.case_status_metrics.total_cases,
                    "pending_human_review_cases": summary.case_status_metrics.pending_human_review_cases,
                    "escalated_cases": summary.case_status_metrics.escalated_cases,
                    "closed_cases": summary.case_status_metrics.closed_cases,
                    "total_overrides": summary.human_override_metrics.total_overrides,
                    "policy_citation_accuracy_available": True,
                },
                {
                    "override_rate_percentage": summary.human_override_metrics.override_rate_percentage,
                    "ai_human_match_rate_percentage": summary.human_override_metrics.ai_human_match_rate_percentage,
                    "average_investigation_duration_seconds": summary.investigation_time_metrics.average_ai_investigation_duration_seconds,
                    "average_human_review_wait_time_seconds": summary.human_review_time_metrics.average_human_review_wait_time_seconds,
                    "policy_citation_accuracy_percentage": summary.policy_citation_metrics.policy_reference_rate_percentage,
                },
            )
        except Exception:
            return None


metrics_service = MetricsService()
