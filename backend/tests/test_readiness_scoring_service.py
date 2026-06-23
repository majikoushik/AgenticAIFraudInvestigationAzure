"""
Tests for ReadinessScoringService.
"""
import pytest
from app.readiness.readiness_scoring_service import ReadinessScoringService

svc = ReadinessScoringService()

_PASS_BLOCKER = {"status": "PASS", "severity": "BLOCKER"}
_FAIL_BLOCKER = {"status": "FAIL", "severity": "BLOCKER"}
_FAIL_HIGH = {"status": "FAIL", "severity": "HIGH"}
_WARN_HIGH = {"status": "WARNING", "severity": "HIGH"}
_PASS_MEDIUM = {"status": "PASS", "severity": "MEDIUM"}
_MANUAL_MEDIUM = {"status": "MANUAL_REVIEW_REQUIRED", "severity": "MEDIUM"}


def test_category_score_all_pass():
    results = [_PASS_BLOCKER, _PASS_BLOCKER, _PASS_MEDIUM]
    score = svc.calculate_category_score(results)
    assert score == 100.0


def test_category_score_all_fail():
    results = [_FAIL_BLOCKER, _FAIL_HIGH]
    score = svc.calculate_category_score(results)
    assert score == 0.0


def test_category_score_mixed():
    results = [_PASS_BLOCKER, _FAIL_HIGH, _PASS_MEDIUM]
    score = svc.calculate_category_score(results)
    assert 0 < score < 100


def test_category_score_excludes_not_applicable():
    results = [{"status": "NOT_APPLICABLE", "severity": "HIGH"}, _PASS_MEDIUM]
    score = svc.calculate_category_score(results)
    assert score == 100.0


def test_count_blockers():
    results = [_FAIL_BLOCKER, _FAIL_BLOCKER, _FAIL_HIGH, _PASS_BLOCKER]
    assert svc.count_blockers(results) == 2


def test_count_high_risks():
    results = [_FAIL_HIGH, _WARN_HIGH, _PASS_MEDIUM, _FAIL_BLOCKER]
    assert svc.count_high_risks(results) == 2


def test_go_live_decision_not_ready_with_blockers():
    assessment = {
        "overall_score": 95.0,
        "blocking_issue_count": 1,
        "high_risk_count": 0,
        "manual_review_required_count": 0,
        "total_checks": 10,
    }
    decision = svc.determine_go_live_decision(assessment)
    assert decision == "NOT_READY"


def test_go_live_decision_ready():
    assessment = {
        "overall_score": 92.0,
        "blocking_issue_count": 0,
        "high_risk_count": 0,
        "manual_review_required_count": 0,
        "total_checks": 10,
    }
    decision = svc.determine_go_live_decision(assessment)
    assert decision == "READY"


def test_go_live_decision_ready_with_risks():
    assessment = {
        "overall_score": 75.0,
        "blocking_issue_count": 0,
        "high_risk_count": 2,
        "manual_review_required_count": 1,
        "total_checks": 10,
    }
    decision = svc.determine_go_live_decision(assessment)
    assert decision == "READY_WITH_RISKS"


def test_summary_message_ready():
    msg = svc.build_summary_message("READY", 95.0, 0, 0, 0)
    assert "ready" in msg.lower()
    assert "95.0" in msg
