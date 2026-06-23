"""
Readiness Scoring Service.
Calculates category and overall readiness scores, determines go-live decision.
"""
from __future__ import annotations

from app.readiness.readiness_config import readiness_config

# Score per status
_STATUS_SCORES: dict[str, float | None] = {
    "PASS": 100.0,
    "WARNING": 60.0,
    "MANUAL_REVIEW_REQUIRED": 50.0,
    "NOT_CHECKED": 40.0,
    "FAIL": 0.0,
    "NOT_APPLICABLE": None,   # Excluded from scoring
}

# Severity weight multipliers (higher severity = more impact on score)
_SEVERITY_WEIGHTS: dict[str, float] = {
    "BLOCKER": 3.0,
    "HIGH": 2.0,
    "MEDIUM": 1.5,
    "LOW": 1.0,
    "INFO": 0.5,
}


class ReadinessScoringService:
    """Calculates readiness scores and go-live decisions."""

    def calculate_category_score(self, results: list[dict]) -> float:
        """
        Weighted average score for a category.
        NOT_APPLICABLE checks are excluded.
        """
        weighted_sum = 0.0
        weight_total = 0.0
        for r in results:
            raw_score = _STATUS_SCORES.get(r.get("status", "NOT_CHECKED"))
            if raw_score is None:
                continue   # NOT_APPLICABLE excluded
            weight = _SEVERITY_WEIGHTS.get(r.get("severity", "MEDIUM"), 1.5)
            weighted_sum += raw_score * weight
            weight_total += weight
        if weight_total == 0:
            return 100.0
        return round(weighted_sum / weight_total, 2)

    def calculate_overall_score(self, category_results: list[dict]) -> float:
        """
        Average of category scores (equal weighting between categories).
        """
        if not category_results:
            return 0.0
        total = sum(cr.get("score", 0.0) for cr in category_results)
        return round(total / len(category_results), 2)

    def count_blockers(self, results: list[dict]) -> int:
        """Count checks with severity=BLOCKER and status=FAIL."""
        return sum(
            1 for r in results
            if r.get("severity") == "BLOCKER" and r.get("status") == "FAIL"
        )

    def count_high_risks(self, results: list[dict]) -> int:
        """Count checks with severity=HIGH and status in (FAIL, WARNING)."""
        return sum(
            1 for r in results
            if r.get("severity") == "HIGH" and r.get("status") in ("FAIL", "WARNING")
        )

    def count_warnings(self, results: list[dict]) -> int:
        return sum(1 for r in results if r.get("status") == "WARNING")

    def count_manual_review(self, results: list[dict]) -> int:
        return sum(1 for r in results if r.get("status") == "MANUAL_REVIEW_REQUIRED")

    def determine_go_live_decision(self, assessment: dict) -> str:
        """
        Determine the go-live decision based on score, blockers, and high risks.

        Rules (in priority order):
        1. Any BLOCKER FAIL → NOT_READY
        2. Overall score >= min_score and no blockers and no high risks → READY
        3. No blockers, high risks <= threshold → READY_WITH_RISKS
        4. Many MANUAL_REVIEW_REQUIRED → MANUAL_REVIEW_REQUIRED
        5. Else → NOT_READY
        """
        cfg = readiness_config
        blocking_count = assessment.get("blocking_issue_count", 0)
        high_risk_count = assessment.get("high_risk_count", 0)
        overall_score = assessment.get("overall_score", 0.0)
        manual_count = assessment.get("manual_review_required_count", 0)
        total_checks = assessment.get("total_checks", 1)

        # Rule 1: Any blocker fail → NOT_READY
        if blocking_count > cfg.max_blockers_for_ready:
            return "NOT_READY"

        # Rule 2: Score above threshold with no high risks → READY
        if overall_score >= cfg.min_score_for_ready and high_risk_count == 0:
            return "READY"

        # Rule 3: No blockers, high risks within tolerance → READY_WITH_RISKS
        if blocking_count == 0 and high_risk_count <= cfg.max_high_risks_for_ready_with_risks:
            return "READY_WITH_RISKS"

        # Rule 4: Many manual items pending → MANUAL_REVIEW_REQUIRED
        if total_checks > 0 and manual_count / total_checks > 0.3:
            return "MANUAL_REVIEW_REQUIRED"

        # Rule 5: Default NOT_READY
        return "NOT_READY"

    def build_summary_message(self, decision: str, overall_score: float,
                               blocking_count: int, high_risk_count: int,
                               manual_count: int) -> str:
        if decision == "READY":
            return f"System is ready for production. Score: {overall_score:.1f}/100."
        if decision == "READY_WITH_RISKS":
            return (
                f"System may proceed with {high_risk_count} high-risk item(s) "
                f"acknowledged. Score: {overall_score:.1f}/100. Review risk register before go-live."
            )
        if decision == "MANUAL_REVIEW_REQUIRED":
            return (
                f"Production readiness requires manual review for {manual_count} item(s). "
                f"Score: {overall_score:.1f}/100."
            )
        return (
            f"System is NOT ready for production. {blocking_count} blocker(s) must be resolved. "
            f"Score: {overall_score:.1f}/100."
        )


# Singleton
readiness_scoring_service = ReadinessScoringService()
