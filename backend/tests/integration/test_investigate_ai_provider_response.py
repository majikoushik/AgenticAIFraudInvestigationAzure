from fastapi.testclient import TestClient

from app.core.constants import CaseStatus
from app.main import app
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service


client = TestClient(app)


def test_investigate_response_includes_ai_provider_metadata() -> None:
    case_status_service.force_status("case-002", CaseStatus.NEW)
    audit_service.clear_case("case-002")
    CaseService._ai_recommendations.pop("case-002", None)
    CaseService._investigation_summaries.pop("case-002", None)

    response = client.post("/api/v1/cases/case-002/investigate")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ai_provider"] in {"local", "azure_openai", "foundry_agent_service"}
    assert payload["human_review_required"] is True
    assert payload["token_usage"]["total_tokens"] >= 0
    assert "safety_flags" in payload
