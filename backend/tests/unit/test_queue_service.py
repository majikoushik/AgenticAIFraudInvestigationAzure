from app.assignment.assignment_repository import AssignmentRepository
from app.assignment.queue_service import QueueService
from app.repositories.case_repository import CaseRepository
from app.repositories.json_repository import JsonRepository


def repository(tmp_path) -> AssignmentRepository:
    JsonRepository(tmp_path).write_list("fraud_alerts.json", [
        {"case_id": "case-1", "alert_id": "a1", "severity": "high", "status": "NEW", "reason": "r", "created_at": "2026-06-01T00:00:00Z", "assigned_to": None, "assignment_status": "UNASSIGNED", "assignment_priority": "HIGH", "sla_status": "NOT_APPLICABLE"},
        {"case_id": "case-2", "alert_id": "a2", "severity": "low", "status": "NEW", "reason": "r", "created_at": "2026-06-02T00:00:00Z", "assigned_to": "fraud_analyst_01", "assignment_status": "ASSIGNED", "assignment_priority": "LOW", "sla_status": "ON_TRACK"},
    ])
    return AssignmentRepository(CaseRepository(JsonRepository(tmp_path)))


def test_unassigned_queue_returns_only_unassigned_cases(tmp_path) -> None:
    queue = QueueService(repository(tmp_path)).get_unassigned_queue()

    assert queue["count"] == 1
    assert queue["cases"][0]["case_id"] == "case-1"


def test_my_queue_returns_current_user_cases(tmp_path) -> None:
    queue = QueueService(repository(tmp_path)).get_my_queue("fraud_analyst_01")

    assert queue["count"] == 1
    assert queue["cases"][0]["case_id"] == "case-2"
