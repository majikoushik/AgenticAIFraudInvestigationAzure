"""
Readiness Risk Service.
Manages the go-live risk register stored in a local JSON file.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.readiness.readiness_config import readiness_config

logger = logging.getLogger(__name__)

_HIGH_SEVERITY_STATUSES = {"FAIL", "WARNING"}


class ReadinessRiskService:
    """CRUD operations for the production readiness risk register."""

    def __init__(self, store_path: Path | None = None) -> None:
        self.store_path = store_path or readiness_config.resolved_risk_register_store_path()

    def _load(self) -> dict:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            return {"risks": []}
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Failed to load risk register; starting fresh.")
            return {"risks": []}

    def _save(self, data: dict) -> None:
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            self.store_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            logger.exception("Failed to save risk register.")

    def create_risk(self, title: str, description: str, category: str, severity: str,
                    owner: str, mitigation_plan: str | None = None,
                    target_date: str | None = None,
                    created_by: str | None = None,
                    assessment_id: str | None = None,
                    check_id: str | None = None) -> dict:
        now = datetime.now(UTC).isoformat()
        risk = {
            "risk_id": f"RISK-{uuid4().hex[:10].upper()}",
            "title": title,
            "description": description,
            "category": category,
            "severity": severity,
            "status": "OPEN",
            "owner": owner,
            "mitigation_plan": mitigation_plan,
            "target_date": target_date,
            "created_at": now,
            "updated_at": now,
            "created_by": created_by,
            "assessment_id": assessment_id,
            "check_id": check_id,
            "close_comment": None,
        }
        data = self._load()
        data["risks"].append(risk)
        self._save(data)
        return risk

    def list_risks(self, status: str | None = None, category: str | None = None,
                   severity: str | None = None) -> list[dict]:
        data = self._load()
        risks = data.get("risks", [])
        if status:
            risks = [r for r in risks if r.get("status") == status]
        if category:
            risks = [r for r in risks if r.get("category") == category]
        if severity:
            risks = [r for r in risks if r.get("severity") == severity]
        return sorted(risks, key=lambda r: r.get("created_at", ""), reverse=True)

    def get_risk(self, risk_id: str) -> dict | None:
        data = self._load()
        for r in data["risks"]:
            if r.get("risk_id") == risk_id:
                return r
        return None

    def update_risk(self, risk_id: str, updates: dict, updated_by: str | None = None) -> dict | None:
        data = self._load()
        for i, r in enumerate(data["risks"]):
            if r.get("risk_id") == risk_id:
                allowed_fields = {
                    "title", "description", "severity", "status",
                    "owner", "mitigation_plan", "target_date", "close_comment"
                }
                for k, v in updates.items():
                    if k in allowed_fields:
                        data["risks"][i][k] = v
                data["risks"][i]["updated_at"] = datetime.now(UTC).isoformat()
                self._save(data)
                return data["risks"][i]
        return None

    def close_risk(self, risk_id: str, closed_by: str | None = None, comment: str | None = None) -> dict | None:
        return self.update_risk(
            risk_id,
            {"status": "CLOSED", "close_comment": comment},
            updated_by=closed_by,
        )

    def create_risks_from_failed_checks(self, assessment: dict,
                                        created_by: str | None = None) -> list[dict]:
        """
        Auto-create risk items for BLOCKER/HIGH checks that FAILED.
        Returns list of created risk dicts.
        """
        created = []
        assessment_id = assessment.get("assessment_id")
        for cat_result in assessment.get("category_results", []):
            for check in cat_result.get("checks", []):
                if (check.get("status") == "FAIL" and
                        check.get("severity") in ("BLOCKER", "HIGH")):
                    # Check if risk already exists for this check+assessment
                    existing = [r for r in self.list_risks()
                                if r.get("check_id") == check.get("check_id")
                                and r.get("assessment_id") == assessment_id]
                    if existing:
                        continue
                    risk = self.create_risk(
                        title=f"[{check.get('check_id')}] {check.get('title')}",
                        description=check.get("message", ""),
                        category=check.get("category", ""),
                        severity=check.get("severity", "HIGH"),
                        owner=_infer_owner(check.get("category", "")),
                        mitigation_plan=check.get("remediation", ""),
                        created_by=created_by,
                        assessment_id=assessment_id,
                        check_id=check.get("check_id"),
                    )
                    created.append(risk)
        return created


def _infer_owner(category: str) -> str:
    _category_owners = {
        "SECURITY": "Security Team",
        "IDENTITY_AND_ACCESS": "Identity Team",
        "SECRETS_AND_KEY_MANAGEMENT": "Platform Team",
        "AI_SAFETY_AND_GUARDRAILS": "AI Governance Team",
        "AUDIT_AND_COMPLIANCE": "Compliance Team",
        "DATA_RETENTION": "Compliance Team",
        "DEVOPS_AND_RELEASE_MANAGEMENT": "DevOps Team",
    }
    return _category_owners.get(category, "Platform Team")


# Singleton
readiness_risk_service = ReadinessRiskService()
