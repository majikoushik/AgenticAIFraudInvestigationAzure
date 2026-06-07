from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_provider_endpoint_does_not_expose_secrets() -> None:
    response = client.get("/api/v1/agents/provider")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ai_provider"] in {"local", "azure_openai", "foundry_agent_service"}
    assert payload["human_review_required"] is True
    assert "api_key" not in response.text.lower()
    assert "secret" not in response.text.lower()
