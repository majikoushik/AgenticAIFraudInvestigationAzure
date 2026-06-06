from app.repositories.audit_repository import AuditRepository


def test_audit_repository_creates_file_if_missing(tmp_path) -> None:
    file_path = tmp_path / "audit_events.json"

    AuditRepository(file_path)

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "[]"


def test_append_and_list_audit_event(tmp_path) -> None:
    repository = AuditRepository(tmp_path / "audit_events.json")

    repository.append_event({"audit_id": "AUDIT-1", "case_id": "case-001", "event_type": "CASE_VIEWED", "actor_role": "SYSTEM", "timestamp": "2026-01-01T00:00:00Z"})

    assert len(repository.list_events_by_case_id("case-001")) == 1


def test_search_by_event_type_and_actor_role(tmp_path) -> None:
    repository = AuditRepository(tmp_path / "audit_events.json")
    repository.append_event({"audit_id": "AUDIT-1", "case_id": "case-001", "event_type": "CASE_VIEWED", "actor_role": "SYSTEM", "timestamp": "2026-01-01T00:00:00Z"})
    repository.append_event({"audit_id": "AUDIT-2", "case_id": "case-002", "event_type": "SECURITY_EVENT", "actor_role": "AUDITOR", "timestamp": "2026-01-02T00:00:00Z"})

    assert len(repository.search_events(event_type="CASE_VIEWED")) == 1
    assert len(repository.search_events(actor_role="AUDITOR")) == 1
