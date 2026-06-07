from datetime import datetime, timedelta, timezone

from app.cost.cost_anomaly_detector import CostAnomalyDetector
from app.cost.cost_config import cost_monitoring_config
from app.cost.cost_repository import CostRepository


def test_cost_anomaly_detector_returns_not_enough_data(tmp_path) -> None:
    result = CostAnomalyDetector(CostRepository(str(tmp_path / "cost_records.json"))).detect_daily_cost_anomaly()

    assert result["status"] == "NOT_ENOUGH_DATA"


def test_cost_anomaly_detector_detects_daily_cost_spike(tmp_path) -> None:
    original = (cost_monitoring_config.anomaly_min_baseline_days, cost_monitoring_config.anomaly_percent_increase_threshold)
    object.__setattr__(cost_monitoring_config, "anomaly_min_baseline_days", 3)
    object.__setattr__(cost_monitoring_config, "anomaly_percent_increase_threshold", 50)
    repository = CostRepository(str(tmp_path / "cost_records.json"))
    today = datetime.now(timezone.utc).date()
    for offset in [1, 2, 3]:
        repository.append_cost_record({"cost_id": f"COST-B{offset}", "usage_id": f"TOK-B{offset}", "case_id": "case-1", "agent_name": "Agent", "operation_name": "op", "ai_provider": "local", "model_or_deployment": "model", "total_tokens": 1, "estimated_total_cost": 10.0, "created_at": f"{(today - timedelta(days=offset)).isoformat()}T00:00:00Z", "metadata": {}})
    repository.append_cost_record({"cost_id": "COST-T", "usage_id": "TOK-T", "case_id": "case-1", "agent_name": "Agent", "operation_name": "op", "ai_provider": "local", "model_or_deployment": "model", "total_tokens": 1, "estimated_total_cost": 20.0, "created_at": f"{today.isoformat()}T00:00:00Z", "metadata": {}})

    try:
        result = CostAnomalyDetector(repository).detect_daily_cost_anomaly()
    finally:
        object.__setattr__(cost_monitoring_config, "anomaly_min_baseline_days", original[0])
        object.__setattr__(cost_monitoring_config, "anomaly_percent_increase_threshold", original[1])

    assert result["status"] == "ANOMALY"
