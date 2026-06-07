from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_telemetry_middleware_adds_correlation_id() -> None:
    response = client.get("/health", headers={"X-Correlation-ID": "test-correlation"})

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "test-correlation"
