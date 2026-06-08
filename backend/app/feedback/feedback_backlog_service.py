import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.core.constants import AuditEventType, FeedbackIssueType, FeedbackSeverity, ReviewerRole
from app.feedback.feedback_sanitizer import sanitize_feedback_payload
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service


class FeedbackBacklogService:
    def __init__(self, store_path: Path | None = None) -> None:
        self.path = store_path or self._resolve(settings.feedback_backlog_store_path)

    def create_backlog_item_from_feedback(self, feedback: dict) -> dict:
        now = datetime.now(UTC).isoformat()
        backlog_type = self.get_recommended_backlog_type(feedback)
        item = {
            "backlog_id": f"AIBL-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "feedback_id": feedback["feedback_id"],
            "backlog_type": backlog_type,
            "title": self._title(backlog_type, feedback),
            "description": feedback.get("comment") or "Review AI feedback and create an improvement action.",
            "priority": feedback.get("severity", FeedbackSeverity.MEDIUM.value),
            "status": "OPEN",
            "owner": "AI Quality Team",
            "created_at": now,
            "updated_at": now,
            "metadata": sanitize_feedback_payload({
                "case_id": feedback.get("case_id"),
                "target_type": feedback.get("target_type"),
                "issue_types": feedback.get("issue_types", []),
                "agent_name": feedback.get("agent_name"),
            }),
        }
        data = self._read()
        data["backlog_items"].append(item)
        self._write(data)
        audit_service.record_event(feedback.get("case_id"), AuditEventType.AI_FEEDBACK_BACKLOG_CREATED, "system", ReviewerRole.SYSTEM, metadata={"feedback_id": feedback.get("feedback_id"), "backlog_id": item["backlog_id"], "backlog_type": backlog_type})
        get_telemetry_client().track_event(telemetry_events.AI_FEEDBACK_BACKLOG_CREATED, {"backlog_type": backlog_type, "severity": item["priority"]}, {"backlog_count": 1})
        return item

    def list_backlog_items(self, filters: dict | None = None) -> list[dict]:
        items = sorted(self._read().get("backlog_items", []), key=lambda item: str(item.get("created_at")), reverse=True)
        filters = filters or {}
        for key in ("status", "backlog_type", "priority", "feedback_id"):
            if filters.get(key):
                items = [item for item in items if str(item.get(key)) == str(filters[key])]
        return items

    def update_backlog_status(self, backlog_id: str, status: str, updated_by: str, comment: str | None = None) -> dict:
        data = self._read()
        for item in data.get("backlog_items", []):
            if item.get("backlog_id") == backlog_id:
                item["status"] = status
                item["updated_at"] = datetime.now(UTC).isoformat()
                item.setdefault("metadata", {})["last_updated_by"] = updated_by
                if comment:
                    item["metadata"]["status_comment"] = comment[:500]
                self._write(data)
                return item
        raise KeyError(backlog_id)

    def get_recommended_backlog_type(self, feedback: dict) -> str:
        issues = set(feedback.get("issue_types", []))
        if issues.intersection({FeedbackIssueType.HALLUCINATION_SUSPECTED.value, FeedbackIssueType.SAFETY_CONCERN.value, FeedbackIssueType.PII_CONCERN.value, FeedbackIssueType.PROMPT_INJECTION_CONCERN.value}):
            return "SAFETY_REVIEW"
        if issues.intersection({FeedbackIssueType.WRONG_POLICY_CITATION.value, FeedbackIssueType.MISSING_POLICY_CITATION.value, FeedbackIssueType.IRRELEVANT_SIMILAR_CASE.value, FeedbackIssueType.MISSING_SIMILAR_CASE.value}):
            return "RAG_IMPROVEMENT"
        if issues.intersection({FeedbackIssueType.INCORRECT_RECOMMENDATION.value, FeedbackIssueType.POOR_EXPLANATION.value, FeedbackIssueType.TOO_VERBOSE.value, FeedbackIssueType.TOO_SHORT.value}):
            return "PROMPT_IMPROVEMENT"
        if FeedbackIssueType.MISSING_EVIDENCE.value in issues:
            return "EVALUATION_CASE"
        return "DATA_QUALITY_REVIEW"

    def _read(self) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"backlog_items": []})
            return {"backlog_items": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict) and isinstance(data.get("backlog_items"), list):
                return data
        except json.JSONDecodeError:
            pass
        return {"backlog_items": []}

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp_path.replace(self.path)

    @staticmethod
    def _title(backlog_type: str, feedback: dict) -> str:
        target = str(feedback.get("target_type", "AI output")).replace("_", " ").title()
        return f"{backlog_type.replace('_', ' ').title()} for {target}"

    @staticmethod
    def _resolve(path_value: str) -> Path:
        path = Path(path_value)
        return path if path.is_absolute() else Path(__file__).resolve().parents[3] / path
