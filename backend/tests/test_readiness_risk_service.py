"""
Tests for ReadinessRiskService.
"""
import pytest
from pathlib import Path

from app.readiness.readiness_risk_service import ReadinessRiskService


def make_svc(tmp_path: Path) -> ReadinessRiskService:
    return ReadinessRiskService(store_path=tmp_path / "risks.json")


def test_create_and_get_risk(tmp_path):
    svc = make_svc(tmp_path)
    risk = svc.create_risk("Test Risk", "desc", "SECURITY", "HIGH", "Security Team")
    assert risk["title"] == "Test Risk"
    assert risk["status"] == "OPEN"
    assert risk["risk_id"].startswith("RISK-")
    result = svc.get_risk(risk["risk_id"])
    assert result is not None


def test_get_risk_not_found(tmp_path):
    svc = make_svc(tmp_path)
    result = svc.get_risk("RISK-NONEXISTENT")
    assert result is None


def test_list_risks_filter_by_status(tmp_path):
    svc = make_svc(tmp_path)
    r1 = svc.create_risk("R1", "", "SECURITY", "HIGH", "Team")
    r2 = svc.create_risk("R2", "", "SECURITY", "HIGH", "Team")
    svc.close_risk(r2["risk_id"])
    open_risks = svc.list_risks(status="OPEN")
    assert all(r["status"] == "OPEN" for r in open_risks)


def test_close_risk(tmp_path):
    svc = make_svc(tmp_path)
    risk = svc.create_risk("R1", "", "SECURITY", "HIGH", "Team")
    closed = svc.close_risk(risk["risk_id"], comment="Resolved by team")
    assert closed["status"] == "CLOSED"
    assert closed["close_comment"] == "Resolved by team"


def test_update_risk(tmp_path):
    svc = make_svc(tmp_path)
    risk = svc.create_risk("R1", "", "SECURITY", "HIGH", "Team")
    updated = svc.update_risk(risk["risk_id"], {"severity": "MEDIUM"})
    assert updated["severity"] == "MEDIUM"


def test_create_risks_from_failed_checks(tmp_path):
    svc = make_svc(tmp_path)
    assessment = {
        "assessment_id": "READY-001",
        "category_results": [
            {
                "category": "SECURITY",
                "checks": [
                    {
                        "check_id": "SEC-001",
                        "title": "No secrets committed",
                        "status": "FAIL",
                        "severity": "BLOCKER",
                        "message": "Secret pattern found",
                        "remediation": "Remove secrets",
                        "category": "SECURITY",
                    },
                    {
                        "check_id": "SEC-002",
                        "title": "Redaction utility",
                        "status": "FAIL",
                        "severity": "HIGH",
                        "message": "Not found",
                        "remediation": "Create utility",
                        "category": "SECURITY",
                    },
                    {
                        "check_id": "SEC-003",
                        "title": "Health endpoint",
                        "status": "PASS",
                        "severity": "HIGH",
                        "message": "Found",
                        "remediation": "",
                        "category": "SECURITY",
                    },
                ],
            }
        ],
    }
    created = svc.create_risks_from_failed_checks(assessment, created_by="test")
    assert len(created) == 2
    check_ids = [r["check_id"] for r in created]
    assert "SEC-001" in check_ids
    assert "SEC-002" in check_ids
    assert "SEC-003" not in check_ids


def test_no_duplicate_risks_for_same_check(tmp_path):
    svc = make_svc(tmp_path)
    assessment = {
        "assessment_id": "READY-001",
        "category_results": [
            {
                "category": "SECURITY",
                "checks": [
                    {
                        "check_id": "SEC-001",
                        "title": "Test",
                        "status": "FAIL",
                        "severity": "BLOCKER",
                        "message": "msg",
                        "remediation": "fix",
                        "category": "SECURITY",
                    }
                ],
            }
        ],
    }
    created1 = svc.create_risks_from_failed_checks(assessment, "test")
    created2 = svc.create_risks_from_failed_checks(assessment, "test")
    assert len(created1) == 1
    assert len(created2) == 0  # Duplicate suppressed
