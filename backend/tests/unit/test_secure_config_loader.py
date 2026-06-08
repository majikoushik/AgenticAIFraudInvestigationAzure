import pytest

from app.security.environment_secret_provider import EnvironmentSecretProvider
from app.security.secret_config import SecretConfig
from app.security.secure_config_loader import SecureConfigLoader


def test_secure_config_loader_reads_non_secret(monkeypatch) -> None:
    monkeypatch.setenv("DEPLOYMENT_MODE", "local")
    loader = SecureConfigLoader(provider=EnvironmentSecretProvider())
    assert loader.get_value("DEPLOYMENT_MODE") == "local"


def test_secure_config_loader_reads_secret_from_env(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_SEARCH_QUERY_KEY", "query-key")
    loader = SecureConfigLoader(provider=EnvironmentSecretProvider())
    assert loader.get_secret("AZURE_SEARCH_QUERY_KEY") == "query-key"


def test_required_missing_secret_raises_in_production() -> None:
    loader = SecureConfigLoader(config=SecretConfig(deployment_mode="prod"), provider=EnvironmentSecretProvider())
    with pytest.raises(RuntimeError):
        loader.get_secret("MISSING_SECRET", required=True)
