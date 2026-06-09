"""
Readiness Service.
Orchestrates readiness assessments: run checks → score → store → audit → telemetry → risks.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.readiness.readiness_check_runner import readiness_check_runner
from app.readiness.readiness_config import readiness_config
from app.readiness.readiness_evidence_service import readiness_evidence_service
from app.readiness.readiness_registry import get_all_categories, get_checks_by_category
from app.readiness.readiness_report_service import readiness_report_service
from app.readiness.readiness_repository import readiness_repository
from app.readiness.readiness_risk_service import readiness_risk_service
from app.readiness.readiness_scoring_service import readiness_scoring_service

logger = logging.getLogger(__name__)


class ReadinessService:
    """Top-level service for the production readiness framework."""

    def run_assessment(
        self,
        environment: str = "prod",
        categories: list[str] | None = None,
        create_risks: bool = True,
        comment: str | None = None,
        requested_by: str = "system",
    ) -> dict:
        """
        Run a full readiness assessment.
        1. Execute all (or selected) checks.
        2. Aggregate category results.
        3. Calculate scores.
        4. Determine go-live decision.
        5. Persist assessment.
        6. Optionally create risks from failures.
        7. Emit audit + telemetry events.
        """
        assessment_id = f"READY-{uuid4().hex[:12].upper()}"
        started_at = datetime.now(UTC).isoformat()

        self._audit("READINESS_ASSESSMENT_STARTED", assessment_id, requested_by, {
            "environment": environment,
            "categories": categories or "ALL",
        })
        self._telemetry("READINESS_ASSESSMENT_STARTED", assessment_id, environment)

        try:
            # 1. Run checks
            selected_categories = categories or get_all_categories()
            all_check_results: list[dict] = []
            for cat in selected_categories:
                results = readiness_check_runner.run_category(cat, environment, requested_by)
                all_check_results.extend(results)

            # 2. Aggregate by category
            category_results = self._aggregate_categories(all_check_results, selected_categories)

            # 3. Scores
            overall_score = readiness_scoring_service.calculate_overall_score(category_results)
            blocking_count = readiness_scoring_service.count_blockers(all_check_results)
            high_risk_count = readiness_scoring_service.count_high_risks(all_check_results)
            warning_count = readiness_scoring_service.count_warnings(all_check_results)
            manual_count = readiness_scoring_service.count_manual_review(all_check_results)

            # 4. Go-live decision
            partial_assessment = {
                "overall_score": overall_score,
                "blocking_issue_count": blocking_count,
                "high_risk_count": high_risk_count,
                "manual_review_required_count": manual_count,
                "total_checks": len(all_check_results),
            }
            go_live_decision = readiness_scoring_service.determine_go_live_decision(partial_assessment)
            summary = readiness_scoring_service.build_summary_message(
                go_live_decision, overall_score, blocking_count, high_risk_count, manual_count
            )

            # 5. Build top_risks from failed BLOCKER/HIGH checks
            top_risks = [
                f"[{r['check_id']}] {r['title']}"
                for r in all_check_results
                if r.get("severity") in ("BLOCKER", "HIGH") and r.get("status") == "FAIL"
            ][:10]

            assessment = {
                "assessment_id": assessment_id,
                "environment": environment,
                "overall_score": overall_score,
                "go_live_decision": go_live_decision,
                "blocking_issue_count": blocking_count,
                "high_risk_count": high_risk_count,
                "warning_count": warning_count,
                "manual_review_required_count": manual_count,
                "total_checks": len(all_check_results),
                "category_results": category_results,
                "top_risks": top_risks,
                "created_by": requested_by,
                "created_at": started_at,
                "completed_at": datetime.now(UTC).isoformat(),
                "summary": summary,
                "comment": comment,
                "evidence_items": [],
            }

            # 6. Persist
            readiness_repository.append_assessment(assessment)

            # 7. Create risks from failures
            if create_risks:
                try:
                    readiness_risk_service.create_risks_from_failed_checks(assessment, requested_by)
                except Exception:
                    logger.exception("Failed to create risks from assessment failures.")

            # 8. Audit + telemetry
            self._audit("READINESS_ASSESSMENT_COMPLETED", assessment_id, requested_by, {
                "environment": environment,
                "overall_score": overall_score,
                "go_live_decision": go_live_decision,
                "blocking_issue_count": blocking_count,
                "high_risk_count": high_risk_count,
            })
            self._telemetry("READINESS_ASSESSMENT_COMPLETED", assessment_id, environment,
                            overall_score=overall_score, blocking_count=blocking_count,
                            high_risk_count=high_risk_count, warning_count=warning_count,
                            manual_count=manual_count)

            return assessment

        except Exception as exc:
            logger.exception("Readiness assessment failed.")
            self._audit("READINESS_ASSESSMENT_FAILED", assessment_id, requested_by, {
                "error": str(exc)
            })
            raise

    def get_assessment(self, assessment_id: str) -> dict | None:
        return readiness_repository.get_assessment(assessment_id)

    def list_assessments(self, environment: str | None = None, limit: int = 50) -> list[dict]:
        return readiness_repository.list_assessments(environment=environment, limit=limit)

    def get_latest_assessment(self, environment: str | None = None) -> dict | None:
        return readiness_repository.get_latest_assessment(environment=environment)

    def get_category_result(self, assessment_id: str, category: str) -> dict | None:
        assessment = readiness_repository.get_assessment(assessment_id)
        if not assessment:
            return None
        for cat in assessment.get("category_results", []):
            if cat.get("category") == category:
                return cat
        return None

    def get_go_live_decision(self, assessment_id: str) -> dict | None:
        assessment = readiness_repository.get_assessment(assessment_id)
        if not assessment:
            return None
        return {
            "assessment_id": assessment_id,
            "environment": assessment.get("environment"),
            "go_live_decision": assessment.get("go_live_decision"),
            "overall_score": assessment.get("overall_score"),
            "blocking_issue_count": assessment.get("blocking_issue_count"),
            "high_risk_count": assessment.get("high_risk_count"),
            "warning_count": assessment.get("warning_count"),
            "manual_review_required_count": assessment.get("manual_review_required_count"),
            "rationale": assessment.get("summary", ""),
            "created_at": assessment.get("created_at"),
        }

    def export_assessment_report(self, assessment_id: str, format: str = "markdown") -> dict:
        result = readiness_report_service.export_report(assessment_id, format)
        self._audit("READINESS_REPORT_EXPORTED", assessment_id, "system", {
            "format": format,
            "export_path": result.get("export_path", ""),
        })
        self._telemetry("READINESS_REPORT_EXPORTED", assessment_id)
        return result

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _aggregate_categories(self, all_results: list[dict], categories: list[str]) -> list[dict]:
        cat_map: dict[str, list[dict]] = {}
        for r in all_results:
            cat = r.get("category", "UNKNOWN")
            cat_map.setdefault(cat, []).append(r)

        category_results = []
        for cat in categories:
            checks = cat_map.get(cat, [])
            score = readiness_scoring_service.calculate_category_score(checks)
            category_results.append({
                "category": cat,
                "score": score,
                "pass_count": sum(1 for c in checks if c.get("status") == "PASS"),
                "fail_count": sum(1 for c in checks if c.get("status") == "FAIL"),
                "warning_count": sum(1 for c in checks if c.get("status") == "WARNING"),
                "manual_review_count": sum(1 for c in checks if c.get("status") == "MANUAL_REVIEW_REQUIRED"),
                "not_checked_count": sum(1 for c in checks if c.get("status") == "NOT_CHECKED"),
                "not_applicable_count": sum(1 for c in checks if c.get("status") == "NOT_APPLICABLE"),
                "blocker_fail_count": sum(
                    1 for c in checks if c.get("severity") == "BLOCKER" and c.get("status") == "FAIL"
                ),
                "checks": checks,
            })
        return category_results

    def _audit(self, event_type_name: str, assessment_id: str, actor: str, metadata: dict) -> None:
        try:
            from app.core.constants import AuditEventType, ReviewerRole
            from app.services.audit_service import audit_service
            from app.schemas.audit_schema import AuditEventCreate
            audit_service.create_event(AuditEventCreate(
                case_id=None,
                event_type=AuditEventType[event_type_name],
                actor=actor,
                actor_role=ReviewerRole.ADMIN,
                action=event_type_name.replace("_", " ").title(),
                description=f"Readiness assessment {assessment_id}: {event_type_name}",
                metadata={k: str(v) for k, v in metadata.items()},
            ))
        except Exception:
            logger.debug("Audit event %s could not be emitted.", event_type_name)

    def _telemetry(self, event_name: str, assessment_id: str, environment: str = "",
                   overall_score: float = 0, blocking_count: int = 0,
                   high_risk_count: int = 0, warning_count: int = 0,
                   manual_count: int = 0) -> None:
        try:
            from app.observability.telemetry_client import get_telemetry_client
            from app.observability import telemetry_events as te
            client = get_telemetry_client()
            event_const = getattr(te, event_name, event_name)
            client.track_event(event_const, {
                "assessment_id": assessment_id,
                "environment": environment,
                "go_live_decision": "",
            }, {
                "overall_score": overall_score,
                "blocking_issue_count": blocking_count,
                "high_risk_count": high_risk_count,
                "warning_count": warning_count,
                "manual_review_required_count": manual_count,
            })
        except Exception:
            logger.debug("Telemetry event %s could not be emitted.", event_name)


# Singleton
readiness_service = ReadinessService()
