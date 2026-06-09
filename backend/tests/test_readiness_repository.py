"""
Tests for ReadinessRepository.
"""
import json
import pytest
from pathlib import Path

from app.readiness.readiness_repository import ReadinessRepository


def _make_assessment(assessment_id: str = "READY-TEST001", env: str = "prod") -> dict:
    return {
        "assessment_id": assessment_id,
        "environment": env,
        "overall_score": 75.0,
        "go_live_decision": "READY_WITH_RISKS",
        "blocking_issue_count": 0,
        "high_risk_count": 2,
        "warning_count": 5,
        "manual_review_required_count": 3,
        "total_checks": 120,
        "category_results": [],
        "top_risks": [],
        "created_by": "test-user",
        "created_at": "2024-01-01T00:00:00+00:00",
        "summary": "Test assessment",
        "comment": None,
        "evidence_items": [],
    }


def test_append_and_get_assessment(tmp_path):
    repo = ReadinessRepository(store_path=tmp_path / "assessments.json")
    a = _make_assessment("READY-001")
    repo.append_assessment(a)
    result = repo.get_assessment("READY-001")
    assert result is not None
    assert result["assessment_id"] == "READY-001"


def test_get_assessment_not_found(tmp_path):
    repo = ReadinessRepository(store_path=tmp_path / "assessments.json")
    result = repo.get_assessment("NONEXISTENT")
    assert result is None


def test_list_assessments_newest_first(tmp_path):
    repo = ReadinessRepository(store_path=tmp_path / "assessments.json")
    a1 = _make_assessment("READY-001"); a1["created_at"] = "2024-01-01T00:00:00+00:00"
    a2 = _make_assessment("READY-002"); a2["created_at"] = "2024-06-01T00:00:00+00:00"
    repo.append_assessment(a1)
    repo.append_assessment(a2)
    items = repo.list_assessments()
    assert items[0]["assessment_id"] == "READY-002"


def test_list_assessments_filter_by_environment(tmp_path):
    repo = ReadinessRepository(store_path=tmp_path / "assessments.json")
    repo.append_assessment(_make_assessment("READY-001", "prod"))
    repo.append_assessment(_make_assessment("READY-002", "staging"))
    prod = repo.list_assessments(environment="prod")
    assert all(a["environment"] == "prod" for a in prod)
    assert len(prod) == 1


def test_get_latest_assessment(tmp_path):
    repo = ReadinessRepository(store_path=tmp_path / "assessments.json")
    a1 = _make_assessment("READY-001"); a1["created_at"] = "2024-01-01T00:00:00+00:00"
    a2 = _make_assessment("READY-002"); a2["created_at"] = "2024-06-01T00:00:00+00:00"
    repo.append_assessment(a1)
    repo.append_assessment(a2)
    latest = repo.get_latest_assessment()
    assert latest["assessment_id"] == "READY-002"


def test_update_assessment(tmp_path):
    repo = ReadinessRepository(store_path=tmp_path / "assessments.json")
    repo.append_assessment(_make_assessment("READY-001"))
    updated = repo.update_assessment("READY-001", {"overall_score": 99.0})
    assert updated is not None
    assert updated["overall_score"] == 99.0


def test_update_nonexistent_returns_none(tmp_path):
    repo = ReadinessRepository(store_path=tmp_path / "assessments.json")
    result = repo.update_assessment("NONEXISTENT", {})
    assert result is None


def test_creates_store_file_if_missing(tmp_path):
    path = tmp_path / "sub" / "assessments.json"
    repo = ReadinessRepository(store_path=path)
    # Trigger a load to create the file
    repo.append_assessment({"assessment_id": "TEST"})
    assert path.exists()
