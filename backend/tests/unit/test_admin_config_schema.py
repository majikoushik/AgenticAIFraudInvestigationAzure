from app.admin.admin_config_schema import SAFE_CONFIG_REGISTRY


def test_safe_registry_does_not_expose_arbitrary_environment_variables() -> None:
    assert "AZURE_OPENAI_API_KEY" not in SAFE_CONFIG_REGISTRY
    assert "APPLICATIONINSIGHTS_CONNECTION_STRING" not in SAFE_CONFIG_REGISTRY
    assert "RAG_TOP_K" in SAFE_CONFIG_REGISTRY
