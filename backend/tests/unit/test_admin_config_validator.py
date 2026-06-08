from app.admin.admin_config_validator import AdminConfigValidator


def test_unknown_config_key_update_fails() -> None:
    result = AdminConfigValidator().validate_update("UNKNOWN_KEY", "value")

    assert result["valid"] is False


def test_secret_config_update_fails() -> None:
    result = AdminConfigValidator().validate_update("AZURE_OPENAI_API_KEY", "secret")

    assert result["valid"] is False


def test_rag_top_k_validates_min_max() -> None:
    validator = AdminConfigValidator()

    assert validator.validate_update("RAG_TOP_K", 8)["valid"] is True
    assert validator.validate_update("RAG_TOP_K", 100)["valid"] is False


def test_ai_provider_validates_enum_values() -> None:
    validator = AdminConfigValidator()

    assert validator.validate_update("AI_PROVIDER", "local")["valid"] is True
    assert validator.validate_update("AI_PROVIDER", "bad")["valid"] is False
