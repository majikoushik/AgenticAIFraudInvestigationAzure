import pytest

from app.assignment.assignment_history_service import AssignmentHistoryService
from app.assignment.assignment_repository import AssignmentRepository
from app.assignment.assignment_service import AssignmentService
from app.assignment.sla_service import SlaService
from app.auth.current_user import AuthenticatedUser
from app.repositories.audit_repository import AuditRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.json_repository import JsonRepository
from app.schemas.assignment_schema import CaseAcceptRequest, CaseAssignmentRequest, CaseReleaseRequest, CaseReassignmentRequest
from app.services.audit_service import AuditService
from app.services.errors import ApiError


def user(role: str, user_id: str) -> AuthenticatedUser:
    return AuthenticatedUser(user_id=user_id, roles=[role], primary_role=role, auth_mode="local")


def service(tmp_path) -> AssignmentService:
    json_repository = JsonRepository(tmp_path)
    json_repository.write_list("fraud_alerts.json", [
        {"case_id": "case-1", "alert_id": "a1", "severity": "high", "status": "NEW", "reason": "r", "created_at": "2026-06-01T00:00:00Z", "assigned_to": None, "assignment_status": "UNASSIGNED", "assignment_priority": "HIGH"},
        {"case_id": "case-closed", "alert_id": "a2", "severity": "low", "status": "CLOSED", "reason": "r", "created_at": "2026-06-01T00:00:00Z", "assigned_to": None, "assignment_status": "UNASSIGNED", "assignment_priority": "LOW"},
    ])
    repository = AssignmentRepository(CaseRepository(json_repository))
    history = AssignmentHistoryService(tmp_path / "assignment_history.json")
    audit = AuditService(AuditRepository(tmp_path / "audit_events.json"))
    return AssignmentService(repository, history, SlaService(repository), audit)


def assign_request(target: str = "fraud_analyst_01") -> CaseAssignmentRequest:
    return CaseAssignmentRequest(case_id="case-1", assigned_to=target, assigned_to_name=target, assigned_to_role="FRAUD_ANALYST", assigned_team="Fraud Operations", assignment_priority="HIGH", comment="assign")


def test_manager_can_assign_unassigned_case(tmp_path) -> None:
    result = service(tmp_path).assign_case(assign_request(), user("FRAUD_MANAGER", "fraud_manager_01"))

    assert result["assignment"]["assigned_to"] == "fraud_analyst_01"
    assert result["assignment"]["assignment_status"] == "ASSIGNED"


def test_analyst_can_self_assign_if_enabled(tmp_path) -> None:
    result = service(tmp_path).assign_case(assign_request(), user("FRAUD_ANALYST", "fraud_analyst_01"))

    assert result["assignment"]["assigned_to"] == "fraud_analyst_01"


def test_analyst_cannot_assign_case_to_another_user(tmp_path) -> None:
    with pytest.raises(ApiError):
        service(tmp_path).assign_case(assign_request("fraud_analyst_02"), user("FRAUD_ANALYST", "fraud_analyst_01"))


def test_manager_can_reassign_case(tmp_path) -> None:
    assignment_service = service(tmp_path)
    assignment_service.assign_case(assign_request(), user("FRAUD_MANAGER", "fraud_manager_01"))

    result = assignment_service.reassign_case("case-1", CaseReassignmentRequest(assigned_to="fraud_analyst_02", assigned_to_name="Fraud Analyst 02", assigned_to_role="FRAUD_ANALYST", assigned_team="Fraud Operations"), user("FRAUD_MANAGER", "fraud_manager_01"))

    assert result["assignment"]["assigned_to"] == "fraud_analyst_02"


def test_assigned_user_can_accept_and_release_case(tmp_path) -> None:
    assignment_service = service(tmp_path)
    assignment_service.assign_case(assign_request(), user("FRAUD_MANAGER", "fraud_manager_01"))
    accepted = assignment_service.accept_case("case-1", CaseAcceptRequest(accepted_by="fraud_analyst_01"), user("FRAUD_ANALYST", "fraud_analyst_01"))

    released = assignment_service.release_case("case-1", CaseReleaseRequest(released_by="fraud_analyst_01", reason="Shift ended"), user("FRAUD_ANALYST", "fraud_analyst_01"))

    assert accepted["assignment"]["assignment_status"] == "ACCEPTED"
    assert released["assignment"]["assigned_to"] is None
    assert released["assignment"]["assignment_status"] == "UNASSIGNED"


def test_closed_case_cannot_be_assigned(tmp_path) -> None:
    request = assign_request()
    request.case_id = "case-closed"

    with pytest.raises(ApiError):
        service(tmp_path).assign_case(request, user("FRAUD_MANAGER", "fraud_manager_01"))


def test_assignment_history_and_audit_event_created(tmp_path) -> None:
    assignment_service = service(tmp_path)
    assignment_service.assign_case(assign_request(), user("FRAUD_MANAGER", "fraud_manager_01"))

    assert assignment_service.history_service.list_history_by_case("case-1")[0]["action"] == "ASSIGNED"
    assert assignment_service.audit_service.get_case_audit_trail("case-1").events[0].event_type == "CASE_ASSIGNED"
