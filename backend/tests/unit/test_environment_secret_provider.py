from app.security.environment_secret_provider import EnvironmentSecretProvider


def test_environment_secret_provider_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "local-placeholder")
    provider = EnvironmentSecretProvider()
    assert provider.get_secret("AZURE_OPENAI_API_KEY") == "local-placeholder"
    assert provider.is_available() is True
    assert provider.provider_name() == "environment"
