from app.assignment.assignment_repository import AssignmentRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.json_repository import JsonRepository


def test_default_assignment_fields_added_safely(tmp_path) -> None:
    JsonRepository(tmp_path).write_list("fraud_alerts.json", [{"case_id": "case-x", "alert_id": "alert-x", "severity": "high"}])
    repository = AssignmentRepository(CaseRepository(JsonRepository(tmp_path)))

    case = repository.get_case("case-x")

    assert case is not None
    assert case["assignment_status"] == "UNASSIGNED"
    assert case["assignment_priority"] == "HIGH"


def test_update_case_assignment_preserves_existing_fields(tmp_path) -> None:
    JsonRepository(tmp_path).write_list("fraud_alerts.json", [{"case_id": "case-x", "alert_id": "alert-x", "severity": "low", "reason": "keep"}])
    repository = AssignmentRepository(CaseRepository(JsonRepository(tmp_path)))

    updated = repository.update_case_assignment("case-x", {"assigned_to": "fraud_analyst_01"})

    assert updated["assigned_to"] == "fraud_analyst_01"
    assert updated["reason"] == "keep"
