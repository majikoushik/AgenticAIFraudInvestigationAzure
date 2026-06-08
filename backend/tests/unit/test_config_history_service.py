from app.admin.config_history_service import ConfigHistoryService


def test_config_history_service_writes_and_filters_records(tmp_path) -> None:
    service = ConfigHistoryService(str(tmp_path / "history.json"))
    service.append_history_record("RAG_TOP_K", 5, 8, "RAG", "admin", "test")

    records = service.list_history(key="RAG_TOP_K")

    assert len(records) == 1
    assert records[0]["old_value"] == 5
    assert records[0]["new_value"] == 8
