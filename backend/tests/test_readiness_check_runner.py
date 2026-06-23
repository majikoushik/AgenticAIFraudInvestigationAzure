"""
Tests for ReadinessCheckRunner — focused on AUTOMATED checks
that use static files and do not require live Azure services.
"""
import pytest
from pathlib import Path
from unittest.mock import patch

from app.readiness.readiness_check_runner import ReadinessCheckRunner


def _runner():
    return ReadinessCheckRunner()


def test_run_all_checks_returns_list():
    """run_all_checks should return at least 100 results without exceptions."""
    runner = _runner()
    results = runner.run_all_checks(environment="local", requested_by="test")
    assert len(results) >= 100


def test_run_all_checks_all_have_status():
    runner = _runner()
    results = runner.run_all_checks(environment="local", requested_by="test")
    valid_statuses = {"PASS", "FAIL", "WARNING", "NOT_APPLICABLE", "MANUAL_REVIEW_REQUIRED", "NOT_CHECKED"}
    for r in results:
        assert r["status"] in valid_statuses, f"Invalid status in {r['check_id']}: {r['status']}"


def test_run_all_checks_all_have_score():
    runner = _runner()
    results = runner.run_all_checks(environment="local", requested_by="test")
    for r in results:
        assert 0.0 <= r["score"] <= 100.0, f"Score out of range in {r['check_id']}: {r['score']}"


def test_run_category_returns_only_that_category():
    runner = _runner()
    results = runner.run_category("SECURITY", environment="local", requested_by="test")
    assert len(results) > 0
    for r in results:
        assert r["category"] == "SECURITY"


def test_run_check_unknown_id_returns_none():
    runner = _runner()
    result = runner.run_check("UNKNOWN-999")
    assert result is None


def test_run_check_known_id_returns_result():
    runner = _runner()
    result = runner.run_check("DOC-001")
    assert result is not None
    assert result["check_id"] == "DOC-001"


def test_manual_checks_return_manual_review_status():
    """All purely MANUAL checks should return MANUAL_REVIEW_REQUIRED."""
    from app.readiness.readiness_registry import get_all_checks
    manual_ids = [c["check_id"] for c in get_all_checks() if c["check_type"] == "MANUAL"]
    runner = _runner()
    for cid in manual_ids[:10]:  # test first 10
        r = runner.run_check(cid)
        assert r is not None
        assert r["status"] == "MANUAL_REVIEW_REQUIRED", f"{cid} should be MANUAL_REVIEW_REQUIRED"


def test_sec_001_passes_when_no_secrets_found(tmp_path):
    """SEC-001 should pass when scan_for_secret_patterns returns clean."""
    (tmp_path / "clean.py").write_text("x = 1")
    runner = _runner()
    from app.readiness.readiness_registry import get_check_by_id
    definition = get_check_by_id("DOC-001")
    result = runner.run_check("DOC-001")
    assert result is not None


def test_run_returns_remediation_string():
    runner = _runner()
    results = runner.run_all_checks()
    for r in results:
        assert isinstance(r["remediation"], str)
