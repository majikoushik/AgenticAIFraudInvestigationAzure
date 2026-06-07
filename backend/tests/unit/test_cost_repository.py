from app.cost.cost_repository import CostRepository


def test_cost_repository_creates_and_appends_records(tmp_path) -> None:
    repository = CostRepository(str(tmp_path / "cost_records.json"))

    token = repository.append_token_usage_record({"usage_id": "TOK-1", "case_id": "case-1", "agent_name": "Agent", "created_at": "2026-01-01T00:00:00Z", "metadata": {"email": "fake@example.invalid"}})
    cost = repository.append_cost_record({"cost_id": "COST-1", "usage_id": "TOK-1", "case_id": "case-1", "agent_name": "Agent", "model_or_deployment": "model", "created_at": "2026-01-01T00:00:00Z", "metadata": {}})

    assert token["usage_id"] == "TOK-1"
    assert cost["cost_id"] == "COST-1"
    assert repository.list_token_usage_records()[0]["metadata"]["email"] == "***MASKED***"
    assert repository.list_by_case_id("case-1")["cost_records"][0]["cost_id"] == "COST-1"


def test_cost_repository_handles_malformed_json(tmp_path) -> None:
    path = tmp_path / "cost_records.json"
    path.write_text("{bad", encoding="utf-8")

    repository = CostRepository(str(path))

    assert repository.list_cost_records() == []
