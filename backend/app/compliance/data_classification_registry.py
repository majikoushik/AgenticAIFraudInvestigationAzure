from app.core.constants import DataCategory, DataClassification


CLASSIFICATION_REGISTRY: dict[DataCategory, tuple[DataClassification, str]] = {
    DataCategory.FRAUD_CASE: (DataClassification.RESTRICTED, "Fraud investigation case data containing sensitive customer and transaction evidence."),
    DataCategory.AUDIT_EVENT: (DataClassification.RESTRICTED, "Audit trail records for regulated decisions and security-sensitive actions."),
    DataCategory.HUMAN_REVIEW: (DataClassification.RESTRICTED, "Human investigator decisions and comments."),
    DataCategory.AI_INVESTIGATION_OUTPUT: (DataClassification.RESTRICTED, "AI-generated investigation package without raw prompts or chain-of-thought."),
    DataCategory.AGENT_TRACE: (DataClassification.CONFIDENTIAL, "Agent execution metadata and deterministic outputs."),
    DataCategory.RAG_RETRIEVAL_RECORD: (DataClassification.CONFIDENTIAL, "Policy retrieval citations and retrieval metadata."),
    DataCategory.POLICY_DOCUMENT: (DataClassification.INTERNAL, "Internal policy documents and references."),
    DataCategory.HISTORICAL_CASE_DOCUMENT: (DataClassification.CONFIDENTIAL, "Synthetic historical fraud case reference records."),
    DataCategory.FEEDBACK_RECORD: (DataClassification.CONFIDENTIAL, "AI feedback from investigators and reviewers."),
    DataCategory.NOTIFICATION_RECORD: (DataClassification.CONFIDENTIAL, "Notification delivery metadata and sanitized payloads."),
    DataCategory.INCIDENT_RECORD: (DataClassification.RESTRICTED, "Operational safety or security incidents."),
    DataCategory.ALERT_RECORD: (DataClassification.CONFIDENTIAL, "Operational and compliance alert records."),
    DataCategory.COST_RECORD: (DataClassification.INTERNAL, "Cost and token usage records."),
    DataCategory.TELEMETRY_RECORD: (DataClassification.INTERNAL, "Operational telemetry events without sensitive payloads."),
    DataCategory.CONFIG_HISTORY: (DataClassification.CONFIDENTIAL, "Administrative configuration change history."),
    DataCategory.ASSIGNMENT_HISTORY: (DataClassification.CONFIDENTIAL, "Case assignment and workload history."),
    DataCategory.EXPORT_FILE: (DataClassification.RESTRICTED, "Compliance export manifests and sanitized evidence packages."),
}


class DataClassificationRegistry:
    def get_classification(self, data_category: str) -> str:
        return CLASSIFICATION_REGISTRY[DataCategory(data_category)][0].value

    def list_classifications(self) -> list[dict]:
        return [
            {"data_category": category.value, "classification": classification.value, "description": description}
            for category, (classification, description) in CLASSIFICATION_REGISTRY.items()
        ]

    def is_restricted(self, data_category: str) -> bool:
        return self.get_classification(data_category) == DataClassification.RESTRICTED.value

    def is_confidential(self, data_category: str) -> bool:
        return self.get_classification(data_category) in {DataClassification.CONFIDENTIAL.value, DataClassification.RESTRICTED.value}


data_classification_registry = DataClassificationRegistry()
