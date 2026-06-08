from app.admin.admin_config_repository import AdminConfigRepository


def test_admin_config_repository_creates_and_updates_non_secret_overrides(tmp_path) -> None:
    repository = AdminConfigRepository(str(tmp_path / "admin_config.json"))

    repository.update_overrides({"RAG_TOP_K": 8, "AZURE_OPENAI_API_KEY": "secret"})

    assert repository.get_override("RAG_TOP_K") == 8
    assert repository.get_override("AZURE_OPENAI_API_KEY") is None


def test_admin_config_repository_reset_overrides(tmp_path) -> None:
    repository = AdminConfigRepository(str(tmp_path / "admin_config.json"))
    repository.update_overrides({"RAG_TOP_K": 8})

    repository.reset_overrides()

    assert repository.get_overrides() == {}
