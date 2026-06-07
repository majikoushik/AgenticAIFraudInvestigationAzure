import json
from pathlib import Path

from app.repositories.audit_repository import AuditRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.json_repository import JsonRepository
from app.services.metrics_service import MetricsService


def build_service(tmp_path: Path, cases: list[dict], events: list[dict]) -> MetricsService:
    (tmp_path / "fraud_alerts.json").write_text(json.dumps(cases), encoding="utf-8")
    audit_path = tmp_path / "audit_events.json"
    audit_path.write_text(json.dumps(events), encoding="utf-8")
    return MetricsService(
        case_repository=CaseRepository(JsonRepository(tmp_path)),
        audit_repository=AuditRepository(audit_path),
    )


def sample_cases() -> list[dict]:
    return [
        {
            "case_id": "case-001",
            "status": "PENDING_HUMAN_REVIEW",
            "created_at": "2026-01-01T00:00:00Z",
            "ai_recommendation": "hold",
            "human_review": {"human_decision": "escalated", "human_override": True, "ai_recommendation": "HOLD"},
            "override_summary": {"has_override": True, "ai_recommendation": "HOLD", "human_decision": "ESCALATE"},
            "policy_references": [{"source": "new-beneficiary-policy.md"}],
        },
        {
            "case_id": "case-002",
            "status": "HELD",
            "created_at": "2026-01-02T00:00:00Z",
            "investigation_summary": {"recommended_action": "approved"},
            "human_review": {"decision": "approve", "human_override": False, "ai_recommendation": "APPROVE"},
        },
        {"case_id": "case-003", "status": "NEW", "created_at": "2026-01-03T00:00:00Z"},
    ]


def sample_events() -> list[dict]:
    return [
        {"case_id": "case-001", "event_type": "AI_INVESTIGATION_STARTED", "timestamp": "2026-01-01T00:00:00Z"},
        {"case_id": "case-001", "event_type": "AI_INVESTIGATION_COMPLETED", "timestamp": "2026-01-01T00:02:00Z"},
        {"case_id": "case-001", "event_type": "PENDING_HUMAN_REVIEW_SET", "new_status": "PENDING_HUMAN_REVIEW", "timestamp": "2026-01-01T00:03:00Z"},
        {"case_id": "case-001", "event_type": "HUMAN_DECISION_SUBMITTED", "human_decision": "ESCALATE", "timestamp": "2026-01-01T00:08:00Z"},
        {"case_id": "case-001", "event_type": "HUMAN_OVERRIDE_DETECTED", "ai_recommendation": "HOLD", "human_decision": "ESCALATE", "timestamp": "2026-01-01T00:08:01Z"},
        {"case_id": "case-001", "event_type": "AGENT_EXECUTION_COMPLETED", "agent_name": "CaseSummaryAgent", "metadata": {"duration_ms": 20}, "timestamp": "2026-01-01T00:01:00Z"},
        {"case_id": "case-001", "event_type": "AGENT_EXECUTION_FAILED", "agent_name": "ReviewerAgent", "timestamp": "2026-01-01T00:01:01Z"},
        {"case_id": "case-001", "event_type": "RAG_RETRIEVAL_COMPLETED", "rag_sources": ["new-beneficiary-policy.md"], "metadata": {"retrieval_mode": "local", "result_count": 2}, "timestamp": "2026-01-01T00:01:02Z"},
        {"case_id": "case-001", "event_type": "RAG_RETRIEVAL_FAILED", "metadata": {"retrieval_mode": "azure_search"}, "timestamp": "2026-01-01T00:01:03Z"},
        {"case_id": "case-001", "event_type": "CASE_STATUS_CHANGED", "event_category": "CASE", "actor_role": "SYSTEM", "timestamp": "2026-01-01T00:01:04Z"},
    ]


def test_case_status_metrics_count_statuses_and_percentages(tmp_path: Path) -> None:
    metrics = build_service(tmp_path, sample_cases(), []).get_case_status_metrics()

    assert metrics.total_cases == 3
    assert metrics.status_counts["NEW"] == 1
    assert metrics.status_counts["HELD"] == 1
    assert metrics.status_percentages["NEW"] == 33.3


def test_safe_percentage_handles_zero_denominator() -> None:
    assert MetricsService.safe_percentage(1, 0) == 0.0


def test_ai_recommendation_metrics_normalize_values(tmp_path: Path) -> None:
    metrics = build_service(tmp_path, sample_cases(), []).get_ai_recommendation_metrics()

    assert metrics.recommendation_counts["HOLD"] == 1
    assert metrics.recommendation_counts["APPROVE"] == 1
    assert metrics.cases_missing_ai_recommendation == 1


def test_human_decision_metrics_normalize_values(tmp_path: Path) -> None:
    metrics = build_service(tmp_path, sample_cases(), sample_events()).get_human_decision_metrics()

    assert metrics.decision_counts["ESCALATE"] == 1
    assert metrics.decision_counts["APPROVE"] == 1
    assert metrics.cases_without_human_decision == 1


def test_override_metrics_calculate_rate_and_pairs(tmp_path: Path) -> None:
    metrics = build_service(tmp_path, sample_cases(), sample_events()).get_human_override_metrics()

    assert metrics.total_reviewed_cases == 2
    assert metrics.total_overrides == 1
    assert metrics.override_rate_percentage == 50.0
    assert metrics.override_pairs == [{"ai_recommendation": "HOLD", "human_decision": "ESCALATE", "count": 1}]


def test_investigation_and_human_review_durations(tmp_path: Path) -> None:
    service = build_service(tmp_path, sample_cases(), sample_events())

    assert service.get_investigation_time_metrics().average_ai_investigation_duration_seconds == 120.0
    assert service.get_human_review_time_metrics().average_human_review_wait_time_seconds == 300.0


def test_agent_and_rag_metrics_count_success_and_failure(tmp_path: Path) -> None:
    service = build_service(tmp_path, sample_cases(), sample_events())

    agent_metrics = service.get_agent_execution_metrics()
    assert agent_metrics.agent_success_count == 1
    assert agent_metrics.agent_failure_count == 1
    assert agent_metrics.average_duration_by_agent["CaseSummaryAgent"] == 20.0

    rag_metrics = service.get_rag_retrieval_metrics()
    assert rag_metrics.rag_success_count == 1
    assert rag_metrics.rag_failure_count == 1
    assert rag_metrics.average_result_count == 2.0


def test_policy_and_audit_metrics_group_values(tmp_path: Path) -> None:
    service = build_service(tmp_path, sample_cases(), sample_events())

    policy_metrics = service.get_policy_citation_metrics()
    assert policy_metrics.cases_with_policy_references == 1
    assert policy_metrics.top_policy_sources[0]["name"] == "new-beneficiary-policy.md"

    audit_metrics = service.get_audit_metrics()
    assert audit_metrics.total_audit_events == len(sample_events())
    assert audit_metrics.audit_events_by_type["CASE_STATUS_CHANGED"] == 1


def test_empty_data_returns_zero_values(tmp_path: Path) -> None:
    service = build_service(tmp_path, [], [])

    assert service.get_case_status_metrics().total_cases == 0
    assert service.get_summary_metrics().audit_metrics.total_audit_events == 0
