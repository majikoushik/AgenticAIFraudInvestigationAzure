from app.compliance.retention_scanner import retention_scanner


class RetentionReviewService:
    def get_review_queue(self, filters: dict | None = None) -> dict:
        filters = filters or {}
        candidates = retention_scanner.latest_candidates()
        for key in ["data_category", "recommended_action", "classification", "legal_hold_status"]:
            if filters.get(key):
                candidates = [item for item in candidates if item.get(key) == filters[key]]
        limit = int(filters.get("limit") or 100)
        return {"count": len(candidates[:limit]), "candidates": candidates[:limit]}

    def mark_candidate_reviewed(self, record_id: str, data_category: str, reviewed_by: str, action: str, comment: str) -> dict:
        return {"record_id": record_id, "data_category": data_category, "reviewed_by": reviewed_by, "action": action, "comment": comment, "status": "REVIEWED"}


retention_review_service = RetentionReviewService()
