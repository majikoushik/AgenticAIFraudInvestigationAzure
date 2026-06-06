from copy import deepcopy

from agents.agents.beneficiary_risk_agent import BeneficiaryRiskAgent
from agents.agents.case_intake_agent import CaseIntakeAgent
from agents.agents.case_summary_agent import CaseSummaryAgent
from agents.agents.customer_profile_agent import CustomerProfileAgent
from agents.agents.device_location_agent import DeviceLocationAgent
from agents.agents.historical_case_agent import HistoricalCaseAgent
from agents.agents.policy_rag_agent import PolicyRagAgent
from agents.agents.reviewer_agent import ReviewerAgent
from agents.agents.transaction_pattern_agent import TransactionPatternAgent
from agents.orchestration.orchestrator import FraudInvestigationOrchestrator
from agents.orchestration.state_manager import StateManager


def sample_case() -> dict:
    return {
        "metadata": {
            "case_id": "case-002",
            "alert_id": "alert-002",
            "severity": "high",
            "reason": "High-value international transfer from a new device to a new beneficiary.",
            "created_at": "2026-01-16T02:20:00Z",
        },
        "customer": {
            "customer_id": "cust-002",
            "display_name": "Synthetic Customer Beta",
            "account_number_masked": "****4321",
            "segment": "small_business",
            "risk_tier": "enhanced_monitoring",
            "home_country": "US",
            "account_opened_date": "2020-09-30",
            "average_transaction_amount": 1800.0,
        },
        "suspicious_transaction": {
            "transaction_id": "txn-002",
            "customer_id": "cust-002",
            "amount": 9500.0,
            "currency": "USD",
            "merchant": "Synthetic Wire Transfer",
            "merchant_country": "GB",
            "timestamp": "2026-01-16T02:14:00Z",
            "channel": "online_banking",
            "payment_method": "wire_transfer",
            "beneficiary_id": "ben-002",
            "device_id": "dev-003",
        },
        "beneficiary": {
            "beneficiary_id": "ben-002",
            "customer_id": "cust-002",
            "display_name": "Synthetic Payee Overseas",
            "relationship_type": "external_account",
            "bank_country": "GB",
            "first_seen": "2026-01-16",
            "risk_note": "New cross-border beneficiary with high-value transfer.",
        },
        "device": {
            "device_id": "dev-003",
            "customer_id": "cust-002",
            "device_type": "browser",
            "trusted": False,
            "last_seen_ip": "203.0.113.55",
            "last_seen_country": "GB",
            "first_seen": "2026-01-16",
        },
        "initial_risk_indicators": [
            {
                "code": "HIGH_VALUE_TRANSFER",
                "description": "Transfer amount is materially above the synthetic customer baseline.",
                "severity": "high",
            }
        ],
        "historical_cases": [],
        "current_status": "awaiting_human_review",
    }


def test_case_intake_agent_validates_required_fields() -> None:
    state = StateManager(sample_case()).state

    output = CaseIntakeAgent().run(state)

    assert output["valid"] is True
    assert output["missing_fields"] == []


def test_case_intake_agent_reports_missing_fields() -> None:
    case = sample_case()
    del case["customer"]["customer_id"]
    state = StateManager(case).state

    output = CaseIntakeAgent().run(state)

    assert output["valid"] is False
    assert "customer.customer_id" in output["missing_fields"]


def test_customer_profile_agent_flags_unusual_amount() -> None:
    state = StateManager(sample_case()).state

    output = CustomerProfileAgent().run(state)

    assert output["is_unusual_amount"] is True
    assert output["risk_indicators"][0]["code"] == "UNUSUAL_CUSTOMER_AMOUNT"


def test_transaction_pattern_agent_generates_indicators() -> None:
    state = StateManager(sample_case()).state

    output = TransactionPatternAgent().run(state)

    codes = {indicator["code"] for indicator in output["risk_indicators"]}
    assert {"HIGH_AMOUNT", "REMOTE_CHANNEL", "NEW_BENEFICIARY_TRANSACTION"}.issubset(codes)


def test_device_location_agent_generates_indicators() -> None:
    state = StateManager(sample_case()).state

    output = DeviceLocationAgent().run(state)

    codes = {indicator["code"] for indicator in output["risk_indicators"]}
    assert {"UNTRUSTED_DEVICE", "UNUSUAL_DEVICE_COUNTRY"}.issubset(codes)


def test_beneficiary_risk_agent_generates_indicators() -> None:
    state = StateManager(sample_case()).state

    output = BeneficiaryRiskAgent().run(state)

    codes = {indicator["code"] for indicator in output["risk_indicators"]}
    assert {"NEW_BENEFICIARY", "BENEFICIARY_RISK_NOTE"}.issubset(codes)


def test_policy_rag_agent_returns_policy_references() -> None:
    manager = StateManager(sample_case())
    manager.record_agent_output("TransactionPatternAgent", TransactionPatternAgent().run(manager.state))
    manager.record_agent_output("BeneficiaryRiskAgent", BeneficiaryRiskAgent().run(manager.state))

    output = PolicyRagAgent().run(manager.state)

    assert output["policy_references"]
    assert any(reference["source_filename"] == "new-beneficiary-policy.md" for reference in output["policy_references"])


def test_historical_case_agent_returns_similar_cases() -> None:
    manager = StateManager(sample_case())
    manager.record_agent_output("TransactionPatternAgent", TransactionPatternAgent().run(manager.state))
    manager.record_agent_output("DeviceLocationAgent", DeviceLocationAgent().run(manager.state))
    manager.record_agent_output("BeneficiaryRiskAgent", BeneficiaryRiskAgent().run(manager.state))

    output = HistoricalCaseAgent().run(manager.state)

    assert output["similar_cases"]
    assert output["similar_cases"][0]["similarity_score"] >= 1


def test_case_summary_agent_generates_structured_summary() -> None:
    manager = build_state_before_summary()

    output = CaseSummaryAgent().run(manager.state)

    assert output["recommended_action"] == "escalate"
    assert output["human_review_requirement"]
    assert output["key_risk_indicators"]
    assert output["llm_provider"] == "local"


def test_reviewer_agent_validates_supported_recommendation() -> None:
    manager = build_state_before_summary()
    manager.record_agent_output("CaseSummaryAgent", CaseSummaryAgent().run(manager.state))

    output = ReviewerAgent().run(manager.state)

    assert output["is_evidence_supported"] is True
    assert output["human_review_required"] is True
    assert "reviewer_notes" in output
    assert "safety_flags" in output


def test_orchestrator_returns_full_investigation_package() -> None:
    package = FraudInvestigationOrchestrator().investigate(deepcopy(sample_case()))

    assert package["case_id"] == "case-002"
    assert len(package["agent_trace"]) == 9
    assert package["policy_references"]
    assert package["reviewer_validation"]["is_evidence_supported"] is True
    assert package["human_review_required"] is True


def build_state_before_summary() -> StateManager:
    manager = StateManager(sample_case())
    for agent in [
        CaseIntakeAgent(),
        CustomerProfileAgent(),
        TransactionPatternAgent(),
        DeviceLocationAgent(),
        BeneficiaryRiskAgent(),
        PolicyRagAgent(),
        HistoricalCaseAgent(),
    ]:
        manager.record_agent_output(agent.name, agent.run(manager.state))
    return manager
