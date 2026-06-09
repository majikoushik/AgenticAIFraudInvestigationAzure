#!/usr/bin/env python3
"""
Production Readiness Assessment Script.
Runs a local readiness assessment, exports a markdown report,
and exits non-zero if the go-live decision is NOT_READY.

Usage:
  python scripts/readiness/run-readiness-assessment.py [OPTIONS]

Options:
  --environment   Target environment (default: prod)
  --categories    Comma-separated list of categories (default: all)
  --no-risks      Skip auto-creating risks from failures
  --fail-on-not-ready  Exit 1 if go-live decision is NOT_READY (default: True)
  --format        Report format: markdown|json (default: markdown)

Example:
  python scripts/readiness/run-readiness-assessment.py --environment prod
  python scripts/readiness/run-readiness-assessment.py --categories SECURITY,IAM
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Add backend to Python path
_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parents[1] / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run production readiness assessment")
    parser.add_argument("--environment", default="prod", help="Target environment")
    parser.add_argument("--categories", default="", help="Comma-separated categories (empty=all)")
    parser.add_argument("--no-risks", action="store_true", help="Skip risk creation")
    parser.add_argument("--fail-on-not-ready", action="store_true", default=True,
                        help="Exit 1 if NOT_READY")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"],
                        help="Report format")
    args = parser.parse_args()

    categories = [c.strip() for c in args.categories.split(",") if c.strip()] or None

    print(f"\n{'='*60}")
    print("  Production Readiness Assessment")
    print(f"  Environment: {args.environment}")
    print(f"  Categories:  {', '.join(categories) if categories else 'ALL'}")
    print(f"{'='*60}\n")

    try:
        from app.readiness.readiness_service import readiness_service

        print("Running assessment...")
        assessment = readiness_service.run_assessment(
            environment=args.environment,
            categories=categories,
            create_risks=not args.no_risks,
            comment="CLI script assessment",
            requested_by="cli-script",
        )

        assessment_id = assessment["assessment_id"]
        overall_score = assessment["overall_score"]
        go_live = assessment["go_live_decision"]
        blocking = assessment["blocking_issue_count"]
        high_risks = assessment["high_risk_count"]
        warnings = assessment["warning_count"]
        manual = assessment["manual_review_required_count"]

        print(f"\n{'='*60}")
        print("  Assessment Results")
        print(f"{'='*60}")
        print(f"  Assessment ID:       {assessment_id}")
        print(f"  Overall Score:       {overall_score:.1f} / 100")
        print(f"  Go-Live Decision:    {go_live}")
        print(f"  Blocking Issues:     {blocking}")
        print(f"  High Risk Items:     {high_risks}")
        print(f"  Warnings:            {warnings}")
        print(f"  Manual Review:       {manual}")
        print(f"\n  Summary: {assessment.get('summary', '')}")
        print(f"{'='*60}\n")

        # Print category scores
        print("Category Scores:")
        for cat in assessment.get("category_results", []):
            score_bar = "█" * int(cat["score"] / 10) + "░" * (10 - int(cat["score"] / 10))
            print(f"  {cat['category']:<40} {score_bar}  {cat['score']:>5.1f}")
        print()

        # Print blockers
        if blocking > 0:
            print("⛔ BLOCKING ISSUES:")
            for cat in assessment.get("category_results", []):
                for check in cat.get("checks", []):
                    if check.get("severity") == "BLOCKER" and check.get("status") == "FAIL":
                        print(f"  - [{check['check_id']}] {check['title']}")
                        print(f"    Remediation: {check['remediation']}")
            print()

        # Export report
        print(f"Exporting {args.format} report...")
        report = readiness_service.export_assessment_report(assessment_id, args.format)
        if "export_path" in report:
            print(f"  Report exported to: {report['export_path']}")
        print()

        # Exit decision
        if args.fail_on_not_ready and go_live == "NOT_READY":
            print("❌ Go-live decision: NOT_READY — exiting with code 1")
            sys.exit(1)
        elif go_live == "READY":
            print("✅ Go-live decision: READY")
        elif go_live == "READY_WITH_RISKS":
            print("⚠️  Go-live decision: READY_WITH_RISKS — review risk register before deploying")
        else:
            print(f"🔵 Go-live decision: {go_live} — manual review required")

        print(f"\nAssessment complete. ID: {assessment_id}\n")

    except Exception as exc:
        print(f"\n❌ Assessment failed: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
