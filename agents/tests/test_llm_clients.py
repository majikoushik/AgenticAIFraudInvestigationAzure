from agents.llm.azure_openai_client import AzureOpenAIClient
from agents.llm.llm_client_factory import LLMClientFactory
from agents.llm.local_llm_client import LocalLLMClient


def test_local_llm_client_works_without_credentials() -> None:
    client = LocalLLMClient()

    assert client.is_available() is True
    assert "Local deterministic response" in client.generate_text("summarize this case")
    assert client.generate_json('{"ok": true}') == {"ok": True}


def test_llm_client_factory_selects_local_by_default(monkeypatch) -> None:
    monkeypatch.delenv("USE_AZURE_OPENAI", raising=False)
    monkeypatch.delenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", raising=False)

    client = LLMClientFactory.create()

    assert isinstance(client, LocalLLMClient)


def test_llm_client_factory_selects_azure_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("USE_AZURE_OPENAI", "true")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "placeholder")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
    monkeypatch.delenv("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", raising=False)

    client = LLMClientFactory.create()

    assert isinstance(client, AzureOpenAIClient)
    assert client.is_available() is True
