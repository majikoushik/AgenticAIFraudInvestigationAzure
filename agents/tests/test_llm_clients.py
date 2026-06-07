from agents.llm.azure_openai_client import AzureOpenAIClient
from agents.llm.llm_errors import LLMConfigurationError
from agents.llm.llm_client_factory import LLMClientFactory
from agents.llm.local_llm_client import LocalLLMClient


def test_local_llm_client_works_without_credentials() -> None:
    client = LocalLLMClient()

    assert client.is_available() is True
    assert "Local deterministic response" in client.generate_text("summarize this case")["content"]
    assert client.generate_json('{"ok": true}')["json"] == {"ok": True}


def test_llm_client_factory_selects_local_by_default(monkeypatch) -> None:
    monkeypatch.delenv("USE_AZURE_OPENAI", raising=False)
    monkeypatch.delenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", raising=False)
    monkeypatch.setenv("AI_PROVIDER", "local")

    client = LLMClientFactory.create()

    assert isinstance(client, LocalLLMClient)


def test_llm_client_factory_selects_azure_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "azure_openai")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "placeholder")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
    monkeypatch.delenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", raising=False)

    client = LLMClientFactory.create()

    assert isinstance(client, AzureOpenAIClient)
    assert client.is_available() is True


def test_llm_client_factory_falls_back_when_azure_missing(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "azure_openai")
    monkeypatch.setenv("AI_PROVIDER_ALLOW_FALLBACK", "true")
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)

    assert isinstance(LLMClientFactory.create(), LocalLLMClient)


def test_llm_client_factory_raises_when_fallback_disabled(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "azure_openai")
    monkeypatch.setenv("AI_PROVIDER_ALLOW_FALLBACK", "false")
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)

    try:
        LLMClientFactory.create()
    except LLMConfigurationError as exc:
        assert "not configured" in str(exc)
    else:
        raise AssertionError("Expected LLMConfigurationError")
