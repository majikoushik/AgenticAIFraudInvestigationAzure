def enforce_human_review(summary: dict) -> dict:
    updated = dict(summary)
    updated["human_review_required"] = True
    updated.setdefault("human_review_requirement", "Human investigator review is required before any high-impact action.")
    return updated
