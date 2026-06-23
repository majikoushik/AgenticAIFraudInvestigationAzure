"""
Tests for readiness registry.
"""
from app.readiness.readiness_registry import (
    get_all_checks,
    get_all_categories,
    get_check_by_id,
    get_checks_by_category,
)


def test_all_checks_not_empty():
    checks = get_all_checks()
    assert len(checks) > 100, "Expected at least 100 checks"


def test_all_checks_have_required_fields():
    checks = get_all_checks()
    required = {"check_id", "category", "title", "description", "check_type",
                "severity", "automated", "manual_evidence_required",
                "recommended_evidence", "remediation", "owner"}
    for c in checks:
        missing = required - c.keys()
        assert not missing, f"Check {c.get('check_id')} missing fields: {missing}"


def test_check_ids_are_unique():
    checks = get_all_checks()
    ids = [c["check_id"] for c in checks]
    assert len(ids) == len(set(ids)), "Duplicate check IDs found"


def test_get_check_by_id_returns_correct():
    c = get_check_by_id("SEC-001")
    assert c is not None
    assert c["check_id"] == "SEC-001"
    assert c["category"] == "SECURITY"


def test_get_check_by_id_returns_none_for_unknown():
    c = get_check_by_id("UNKNOWN-999")
    assert c is None


def test_get_checks_by_category_security():
    checks = get_checks_by_category("SECURITY")
    assert len(checks) > 0
    for c in checks:
        assert c["category"] == "SECURITY"


def test_all_categories_present():
    categories = get_all_categories()
    expected_categories = ["SECURITY", "ARCHITECTURE", "AI_SAFETY_AND_GUARDRAILS", "AUDIT_AND_COMPLIANCE"]
    for cat in expected_categories:
        assert cat in categories, f"Category {cat} missing"


def test_all_severity_values_are_valid():
    valid = {"BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"}
    for c in get_all_checks():
        assert c["severity"] in valid, f"Invalid severity in {c['check_id']}: {c['severity']}"


def test_all_check_type_values_are_valid():
    valid = {"AUTOMATED", "MANUAL", "HYBRID"}
    for c in get_all_checks():
        assert c["check_type"] in valid, f"Invalid check_type in {c['check_id']}: {c['check_type']}"
