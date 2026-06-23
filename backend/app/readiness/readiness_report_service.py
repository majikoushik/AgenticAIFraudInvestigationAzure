"""
Readiness Report Service.
Generates markdown and JSON readiness reports from assessment data.
Exports to data/exports/readiness/{assessment_id}/.

SECURITY: No secrets, raw prompts, raw responses, JWTs, or chain-of-thought are included.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from app.readiness.readiness_config import readiness_config
from app.readiness.readiness_repository import readiness_repository

logger = logging.getLogger(__name__)


class ReadinessReportService:
    """Generates and exports readiness reports in markdown and JSON formats."""

    def generate_markdown_report(self, assessment_id: str) -> dict:
        assessment = readiness_repository.get_assessment(assessment_id)
        if not assessment:
            return {"error": "Assessment not found.", "assessment_id": assessment_id}

        lines = self._build_markdown(assessment)
        content = "\n".join(lines)
        return {
            "assessment_id": assessment_id,
            "format": "markdown",
            "content": content,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def generate_json_report(self, assessment_id: str) -> dict:
        assessment = readiness_repository.get_assessment(assessment_id)
        if not assessment:
            return {"error": "Assessment not found.", "assessment_id": assessment_id}

        # Strip any internal fields that could leak sensitive info
        safe = self._sanitize_assessment(assessment)
        return {
            "assessment_id": assessment_id,
            "format": "json",
            "report": safe,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def export_report(self, assessment_id: str, format: str = "markdown") -> dict:
        """Export report to disk and return metadata."""
        export_dir = readiness_config.resolved_report_export_path() / assessment_id
        export_dir.mkdir(parents=True, exist_ok=True)

        if format == "json":
            report_data = self.generate_json_report(assessment_id)
            if "error" in report_data:
                return report_data
            file_path = export_dir / "production-readiness-report.json"
            file_path.write_text(json.dumps(report_data["report"], indent=2), encoding="utf-8")
            content_preview = json.dumps(report_data["report"])[:500]
        else:
            report_data = self.generate_markdown_report(assessment_id)
            if "error" in report_data:
                return report_data
            file_path = export_dir / "production-readiness-report.md"
            file_path.write_text(report_data["content"], encoding="utf-8")
            content_preview = report_data["content"][:500]

        return {
            "assessment_id": assessment_id,
            "format": format,
            "export_path": str(file_path).replace("\\", "/"),
            "content_preview": content_preview,
            "exported_at": datetime.now(UTC).isoformat(),
        }

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _sanitize_assessment(self, assessment: dict) -> dict:
        """Remove any fields that could expose sensitive data."""
        safe = dict(assessment)
        # Remove raw evidence that might contain sensitive notes
        for cat in safe.get("category_results", []):
            for check in cat.get("checks", []):
                check.pop("automated_result", None)
        return safe

    def _build_markdown(self, assessment: dict) -> list[str]:
        a = assessment
        lines = [
            "# Production Readiness Assessment Report",
            "",
            f"**Assessment ID:** {a.get('assessment_id')}",
            f"**Environment:** {a.get('environment')}",
            f"**Generated:** {a.get('created_at')}",
            f"**Assessed by:** {a.get('created_by')}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"| Metric | Value |",
            "| --- | --- |",
            f"| **Overall Score** | {a.get('overall_score', 0):.1f} / 100 |",
            f"| **Go-Live Decision** | **{a.get('go_live_decision')}** |",
            f"| **Blocking Issues** | {a.get('blocking_issue_count', 0)} |",
            f"| **High Risk Items** | {a.get('high_risk_count', 0)} |",
            f"| **Warnings** | {a.get('warning_count', 0)} |",
            f"| **Manual Review Required** | {a.get('manual_review_required_count', 0)} |",
            "",
            f"> **Summary:** {a.get('summary', '')}",
            "",
            "---",
            "",
            "## Go-Live Decision",
            "",
        ]

        decision = a.get("go_live_decision", "NOT_READY")
        decision_icons = {
            "READY": "✅",
            "READY_WITH_RISKS": "⚠️",
            "NOT_READY": "❌",
            "MANUAL_REVIEW_REQUIRED": "🔵",
        }
        lines.append(f"### {decision_icons.get(decision, '❓')} {decision}")
        lines.append("")

        # Blocking issues
        lines += [
            "---",
            "",
            "## Blocking Issues",
            "",
        ]
        blockers = []
        for cat in a.get("category_results", []):
            for check in cat.get("checks", []):
                if check.get("severity") == "BLOCKER" and check.get("status") == "FAIL":
                    blockers.append(check)
        if blockers:
            for b in blockers:
                lines.append(f"- ❌ **{b['check_id']}**: {b['title']}")
                lines.append(f"  - _Remediation:_ {b.get('remediation', '')}")
        else:
            lines.append("_No blocking issues found._")
        lines.append("")

        # Category scores
        lines += [
            "---",
            "",
            "## Category Scores",
            "",
            "| Category | Score | Pass | Fail | Warning | Manual Review |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for cat in a.get("category_results", []):
            lines.append(
                f"| {cat.get('category')} | {cat.get('score', 0):.1f} | "
                f"{cat.get('pass_count', 0)} | {cat.get('fail_count', 0)} | "
                f"{cat.get('warning_count', 0)} | {cat.get('manual_review_count', 0)} |"
            )
        lines.append("")

        # Category checklists
        lines += [
            "---",
            "",
            "## Category-wise Checklist Results",
            "",
        ]
        for cat in a.get("category_results", []):
            lines.append(f"### {cat.get('category')}")
            lines.append("")
            lines.append("| Check ID | Title | Status | Severity | Message |")
            lines.append("| --- | --- | --- | --- | --- |")
            for check in cat.get("checks", []):
                status_icon = {
                    "PASS": "✅", "FAIL": "❌", "WARNING": "⚠️",
                    "MANUAL_REVIEW_REQUIRED": "🔵", "NOT_CHECKED": "⬜",
                    "NOT_APPLICABLE": "—",
                }.get(check.get("status", ""), "❓")
                msg = check.get("message", "").replace("|", "\\|")[:80]
                lines.append(
                    f"| {check.get('check_id')} | {check.get('title')} | "
                    f"{status_icon} {check.get('status')} | {check.get('severity')} | {msg} |"
                )
            lines.append("")

        # Manual review items
        lines += [
            "---",
            "",
            "## Manual Review Required",
            "",
        ]
        manual_items = []
        for cat in a.get("category_results", []):
            for check in cat.get("checks", []):
                if check.get("status") == "MANUAL_REVIEW_REQUIRED":
                    manual_items.append(check)
        if manual_items:
            for m in manual_items:
                lines.append(f"- 🔵 **{m['check_id']}** ({m.get('category')}): {m.get('title')}")
                lines.append(f"  - _Owner:_ {m.get('remediation', '')}")
        else:
            lines.append("_No manual review items._")
        lines.append("")

        # Sign-off section
        lines += [
            "---",
            "",
            "## Production Go-Live Sign-off",
            "",
            "| Role | Name | Signature | Date |",
            "| --- | --- | --- | --- |",
            "| Solution Architect | | | |",
            "| Security Owner | | | |",
            "| Compliance Owner | | | |",
            "| Fraud Operations Owner | | | |",
            "| Platform Owner | | | |",
            "| Business Sponsor | | | |",
            "",
            "---",
            "",
            f"_Report generated by Production Readiness Framework — {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}_",
            "",
            "> ⚠️ **Disclaimer:** Automated checks are heuristic. Legal and compliance approvals must be manually obtained. Azure live validation may require environment-specific scripts.",
        ]

        return lines


# Singleton
readiness_report_service = ReadinessReportService()
