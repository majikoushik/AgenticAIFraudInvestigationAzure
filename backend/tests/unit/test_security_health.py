from app.security.environment_secret_provider import EnvironmentSecretProvider
from app.security.secret_config import SecretConfig
from app.security.secure_config_loader import SecureConfigLoader
from app.security.security_health import SecurityHealthService


def test_security_health_returns_no_secret_values(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "super-secret")
    loader = SecureConfigLoader(config=SecretConfig(), provider=EnvironmentSecretProvider())
    health = SecurityHealthService(loader).get_security_health()
    assert health["status"] in {"ok", "degraded", "unhealthy"}
    assert "super-secret" not in str(health)
