import json
from pathlib import Path

from app.alerting.alert_evaluator import AlertEvaluator
from app.core.constants import AlertType, CaseStatus


class _Metrics:
    def __init__(self, override_rate: float = 0, citation_rate: float = 100) -> None:
        self.agent_execution_metrics = type("AgentMetrics", (), {"agent_failure_count": 0})()
        self.human_override_metrics = type("OverrideMetrics", (), {"override_rate_percentage": override_rate})()
        self.policy_citation_metrics = type("CitationMetrics", (), {"policy_reference_rate_percentage": citation_rate})()
        self.case_status_metrics = type("CaseMetrics", (), {"total_cases": 1})()


class _MetricsService:
    def __init__(self, metrics: _Metrics | None = None) -> None:
        self.metrics = metrics or _Metrics()

    def get_summary_metrics(self):
        return self.metrics


class _CaseRepository:
    def __init__(self, cases: list[dict] | None = None) -> None:
        self.cases = cases or []

    def list_alerts(self) -> list[dict]:
        return self.cases


def _write_telemetry(records: list[dict]):
    telemetry_path = Path(__file__).resolve().parents[3] / "data" / "synthetic" / "telemetry_events.json"
    original = telemetry_path.read_text(encoding="utf-8") if telemetry_path.exists() else "[]"
    telemetry_path.write_text(json.dumps(records), encoding="utf-8")
    return telemetry_path, original


def test_alert_evaluator_detects_api_error_rate_and_latency() -> None:
    telemetry_path, original = _write_telemetry(
        [
            {"name": "API_REQUEST_COMPLETED", "properties": {"status_code": 500}, "measurements": {"duration_ms": 5000}},
            {"name": "API_REQUEST_COMPLETED", "properties": {"status_code": 200}, "measurements": {"duration_ms": 4000}},
        ]
    )
    try:
        results = AlertEvaluator(_MetricsService(), _CaseRepository()).evaluate_all_rules()
    finally:
        telemetry_path.write_text(original, encoding="utf-8")

    triggered = {result["alert_type"] for result in results if result["status"] == "TRIGGERED"}
    assert AlertType.HIGH_API_ERROR_RATE.value in triggered
    assert AlertType.HIGH_API_LATENCY.value in triggered


def test_alert_evaluator_reports_not_enough_data_when_telemetry_missing() -> None:
    telemetry_path, original = _write_telemetry([])
    try:
        results = AlertEvaluator(_MetricsService(), _CaseRepository()).evaluate_all_rules()
    finally:
        telemetry_path.write_text(original, encoding="utf-8")

    by_type = {result["alert_type"]: result for result in results}
    assert by_type[AlertType.HIGH_API_ERROR_RATE.value]["status"] == "NOT_ENOUGH_DATA"


def test_alert_evaluator_detects_prompt_injection() -> None:
    telemetry_path, original = _write_telemetry([{"name": "PROMPT_INJECTION_DETECTED", "properties": {}, "measurements": {}}])
    try:
        results = AlertEvaluator(_MetricsService(), _CaseRepository()).evaluate_all_rules()
    finally:
        telemetry_path.write_text(original, encoding="utf-8")

    by_type = {result["alert_type"]: result for result in results}
    assert by_type[AlertType.PROMPT_INJECTION_DETECTED.value]["status"] == "TRIGGERED"


def test_alert_evaluator_detects_high_human_override_rate() -> None:
    telemetry_path, original = _write_telemetry([])
    try:
        results = AlertEvaluator(_MetricsService(_Metrics(override_rate=75)), _CaseRepository()).evaluate_all_rules()
    finally:
        telemetry_path.write_text(original, encoding="utf-8")

    by_type = {result["alert_type"]: result for result in results}
    assert by_type[AlertType.HIGH_HUMAN_OVERRIDE_RATE.value]["status"] == "TRIGGERED"


def test_alert_evaluator_detects_stuck_pending_review_case() -> None:
    telemetry_path, original = _write_telemetry([])
    case_repository = _CaseRepository([{"status": CaseStatus.PENDING_HUMAN_REVIEW.value, "status_updated_at": "2020-01-01T00:00:00Z"}])
    try:
        results = AlertEvaluator(_MetricsService(), case_repository).evaluate_all_rules()
    finally:
        telemetry_path.write_text(original, encoding="utf-8")

    by_type = {result["alert_type"]: result for result in results}
    assert by_type[AlertType.CASES_STUCK_PENDING_REVIEW.value]["status"] == "TRIGGERED"
