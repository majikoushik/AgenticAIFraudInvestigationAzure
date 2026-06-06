from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "fraud-investigation-backend",
    }


def test_get_case_list() -> None:
    response = client.get("/api/v1/cases")

    assert response.status_code == 200
    cases = response.json()
    assert len(cases) >= 3
    assert cases[0]["case_id"] == "case-001"


def test_get_case_details() -> None:
    response = client.get("/api/v1/cases/case-001")

    assert response.status_code == 200
    case_detail = response.json()
    assert case_detail["metadata"]["case_id"] == "case-001"
    assert case_detail["customer"]["account_number_masked"] == "****3456"
    assert case_detail["suspicious_transaction"]["transaction_id"] == "txn-001"
    assert case_detail["beneficiary"]["beneficiary_id"] == "ben-001"
    assert case_detail["device"]["trusted"] is False
    assert case_detail["current_status"] == "awaiting_human_review"


def test_submit_decision_records_audit_entry() -> None:
    response = client.post(
        "/api/v1/cases/case-001/decision",
        json={
            "decision": "hold",
            "comment": "Synthetic review requires additional verification.",
            "reviewed_by": "synthetic.reviewer",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "recorded"

    audit_response = client.get("/api/v1/cases/case-001/audit")
    assert audit_response.status_code == 200
    entries = audit_response.json()["entries"]
    assert any(entry["decision"] == "hold" for entry in entries)


def test_investigate_case_returns_agent_package() -> None:
    response = client.post("/api/v1/cases/case-002/investigate")

    assert response.status_code == 200
    package = response.json()
    assert package["case_id"] == "case-002"
    assert len(package["agent_trace"]) == 9
    assert package["risk_indicators"]
    assert package["policy_references"]
    assert package["similar_cases"]
    assert package["investigation_summary"]["recommended_action"] == "escalate"
    assert package["reviewer_validation"]["is_evidence_supported"] is True
    assert package["human_review_required"] is True


def test_policy_search_endpoint_uses_local_fallback() -> None:
    response = client.get("/api/v1/rag/policies/search", params={"query": "new beneficiary review"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "new beneficiary review"
    assert payload["retrieval_mode"] in {"local", "azure_search"}
    assert payload["results"]
    assert "source_filename" in payload["results"][0]


def test_agent_config_endpoint_does_not_expose_secrets() -> None:
    response = client.get("/api/v1/agents/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] in {"local", "azure_openai", "foundry_agent_service"}
    assert "api_key" not in payload
    assert "AZURE_OPENAI_API_KEY" not in response.text


def test_case_not_found() -> None:
    response = client.get("/api/v1/cases/case-missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "case_not_found",
            "message": "Case 'case-missing' was not found.",
        }
    }


def test_invalid_decision_returns_400() -> None:
    response = client.post(
        "/api/v1/cases/case-001/decision",
        json={
            "decision": "freeze",
            "comment": "This unsupported decision should be rejected.",
            "reviewed_by": "synthetic.reviewer",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_decision"
