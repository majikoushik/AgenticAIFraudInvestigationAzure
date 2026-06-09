"""
Readiness Repository.
Persists assessment history in a local JSON file.
Safe write pattern — creates file if missing.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from app.readiness.readiness_config import readiness_config

logger = logging.getLogger(__name__)


class ReadinessRepository:
    """Local JSON persistence for readiness assessment history."""

    def __init__(self, store_path: Path | None = None) -> None:
        self.store_path = store_path or readiness_config.resolved_assessment_store_path()

    def _load(self) -> dict:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            return {"assessments": []}
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Failed to load readiness assessments; starting fresh.")
            return {"assessments": []}

    def _save(self, data: dict) -> None:
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            self.store_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            logger.exception("Failed to save readiness assessments.")

    def append_assessment(self, assessment: dict) -> dict:
        """Append a new assessment to the store. Returns the stored assessment."""
        data = self._load()
        data["assessments"].append(assessment)
        self._save(data)
        return assessment

    def get_assessment(self, assessment_id: str) -> dict | None:
        data = self._load()
        for a in data["assessments"]:
            if a.get("assessment_id") == assessment_id:
                return a
        return None

    def list_assessments(self, environment: str | None = None, limit: int = 50) -> list[dict]:
        """Return assessments sorted newest first."""
        data = self._load()
        assessments = data.get("assessments", [])
        if environment:
            assessments = [a for a in assessments if a.get("environment") == environment]
        # Sort newest first by created_at
        assessments = sorted(assessments, key=lambda a: a.get("created_at", ""), reverse=True)
        return assessments[:limit]

    def get_latest_assessment(self, environment: str | None = None) -> dict | None:
        results = self.list_assessments(environment=environment, limit=1)
        return results[0] if results else None

    def update_assessment(self, assessment_id: str, updates: dict) -> dict | None:
        """Update fields of an existing assessment (e.g., after adding evidence)."""
        data = self._load()
        for i, a in enumerate(data["assessments"]):
            if a.get("assessment_id") == assessment_id:
                data["assessments"][i].update(updates)
                self._save(data)
                return data["assessments"][i]
        return None


# Singleton
readiness_repository = ReadinessRepository()
