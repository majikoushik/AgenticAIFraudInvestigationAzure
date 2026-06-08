from app.assignment.assignment_repository import AssignmentRepository
from app.assignment.workload_service import WorkloadService
from app.repositories.case_repository import CaseRepository
from app.repositories.json_repository import JsonRepository


def test_workload_summary_groups_cases_by_investigator(tmp_path) -> None:
    json_repository = JsonRepository(tmp_path)
    json_repository.write_list("fraud_alerts.json", [
        {"case_id": "case-1", "alert_id": "a1", "severity": "high", "assigned_to": "fraud_analyst_01", "assigned_to_name": "Fraud Analyst 01", "assigned_to_role": "FRAUD_ANALYST", "assigned_team": "Fraud Operations", "assignment_status": "ACCEPTED", "assignment_priority": "HIGH", "sla_status": "ON_TRACK"},
        {"case_id": "case-2", "alert_id": "a2", "severity": "low", "assigned_to": None, "assignment_status": "UNASSIGNED", "assignment_priority": "LOW", "sla_status": "NOT_APPLICABLE"},
    ])
    repository = AssignmentRepository(CaseRepository(json_repository))

    summary = WorkloadService(repository, json_repository).get_workload_summary()

    assert summary["total_assigned_cases"] == 1
    assert summary["total_unassigned_cases"] == 1
    assert summary["active_cases_by_investigator"]["fraud_analyst_01"] == 1
