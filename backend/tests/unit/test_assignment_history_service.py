from app.assignment.assignment_history_service import AssignmentHistoryService


def test_assignment_history_is_created_and_sorted(tmp_path) -> None:
    service = AssignmentHistoryService(tmp_path / "assignment_history.json")

    service.append_history_record({"case_id": "case-001", "action": "ASSIGNED", "actor": "manager", "actor_role": "FRAUD_MANAGER", "comment": "x"})
    service.append_history_record({"case_id": "case-001", "action": "ACCEPTED", "actor": "analyst", "actor_role": "FRAUD_ANALYST", "comment": "y"})

    history = service.list_history_by_case("case-001")

    assert len(history) == 2
    assert history[0]["action"] == "ACCEPTED"
    assert history[0]["history_id"].startswith("ASSIGNHIST-")
