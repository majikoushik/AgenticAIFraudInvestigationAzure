class NotificationRecipientRouter:
    def resolve_recipients(self, event_type: str, context: dict) -> list[dict]:
        if event_type in {"CASE_ASSIGNED", "CASE_REASSIGNED", "CASE_TRANSFERRED"} and context.get("assigned_to"):
            recipients = [{
                "recipient_type": "USER",
                "recipient_id": context["assigned_to"],
                "recipient_role": context.get("assigned_to_role"),
                "recipient_team": context.get("assigned_team"),
            }]
            if context.get("assignment_priority") == "CRITICAL":
                recipients.append({"recipient_type": "ROLE", "recipient_role": "FRAUD_MANAGER", "recipient_id": None, "recipient_team": context.get("assigned_team")})
            return recipients
        if event_type in {"SLA_AT_RISK", "SLA_BREACHED"}:
            recipients = []
            if context.get("assigned_to"):
                recipients.append({"recipient_type": "USER", "recipient_id": context["assigned_to"], "recipient_role": context.get("assigned_to_role"), "recipient_team": context.get("assigned_team")})
            recipients.append({"recipient_type": "ROLE", "recipient_role": "FRAUD_MANAGER", "recipient_id": None, "recipient_team": context.get("assigned_team")})
            return recipients
        if event_type in {"HUMAN_OVERRIDE_DETECTED", "PROMPT_INJECTION_DETECTED", "GUARDRAIL_VIOLATION_DETECTED"}:
            return [{"recipient_type": "ROLE", "recipient_role": "FRAUD_MANAGER"}, {"recipient_type": "ROLE", "recipient_role": "COMPLIANCE_OFFICER"}]
        if event_type in {"ALERT_CREATED", "INCIDENT_CREATED", "BUDGET_WARNING", "BUDGET_EXCEEDED", "ADMIN_CONFIG_UPDATED", "FEATURE_FLAG_UPDATED"}:
            return [{"recipient_type": "ROLE", "recipient_role": "ADMIN"}]
        return [{"recipient_type": "ROLE", "recipient_role": "FRAUD_MANAGER"}]
