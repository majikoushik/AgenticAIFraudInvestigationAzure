"""
Readiness Evidence Service.
Attaches manual evidence to specific checks within a readiness assessment.
Evidence is stored inside the assessment record in the repository.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import uuid4

from app.readiness.readiness_repository import readiness_repository

logger = logging.getLogger(__name__)


class ReadinessEvidenceService:
    """Manages manual evidence attachments for readiness check results."""

    def add_evidence(
        self,
        assessment_id: str,
        check_id: str,
        evidence_type: str,
        description: str,
        submitted_by: str,
        metadata: dict | None = None,
    ) -> dict | None:
        """
        Add evidence to a check result within an existing assessment.
        Returns the created evidence item or None if assessment not found.
        """
        assessment = readiness_repository.get_assessment(assessment_id)
        if not assessment:
            return None

        evidence_item = {
            "evidence_id": f"EVID-{uuid4().hex[:10].upper()}",
            "check_id": check_id,
            "assessment_id": assessment_id,
            "evidence_type": evidence_type,  # TEXT | FILE_REFERENCE | URL | CHECK_OUTPUT
            "description": description,
            "submitted_by": submitted_by,
            "submitted_at": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }

        # Attach evidence to the matching check result inside category_results
        updated = False
        for cat_result in assessment.get("category_results", []):
            for check in cat_result.get("checks", []):
                if check.get("check_id") == check_id:
                    check.setdefault("evidence", []).append(
                        f"[{evidence_type}] {description} (by {submitted_by})"
                    )
                    check.setdefault("manual_notes", description)
                    updated = True
                    break
            if updated:
                break

        # Store at assessment level too for easier retrieval
        assessment.setdefault("evidence_items", []).append(evidence_item)
        readiness_repository.update_assessment(assessment_id, {
            "category_results": assessment.get("category_results", []),
            "evidence_items": assessment.get("evidence_items", []),
        })

        return evidence_item

    def list_evidence(self, assessment_id: str) -> list[dict]:
        """Return all evidence items for an assessment."""
        assessment = readiness_repository.get_assessment(assessment_id)
        if not assessment:
            return []
        return assessment.get("evidence_items", [])


# Singleton
readiness_evidence_service = ReadinessEvidenceService()
