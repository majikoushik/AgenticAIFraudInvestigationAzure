# 5. Human-in-the-Loop Investigation Approval

Date: 2026-06-23

## Status
Accepted

## Context
In a regulated banking environment, fully autonomous AI taking punitive actions (such as freezing accounts) presents unacceptable risk.

## Decision
We designed a strict Human-in-the-Loop (HitL) boundary. The AI agents are authorized only to gather evidence, search policies, and recommend a decision. They transition the case to `PENDING_HUMAN_REVIEW`. A human investigator must then explicitly approve, hold, escalate, or reject the case, providing an override reason if they disagree with the AI.

## Consequences
- **Positive:** Complies with regulatory and safety expectations. Provides a robust dataset of AI-vs-Human agreement for future fine-tuning.
- **Negative:** Adds friction to the investigation workflow, requiring UI and API surface area to manage the review process.
