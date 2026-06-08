from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fraud-investigation-backend"
    environment: str = "local"
    log_level: str = "info"
    log_format: str = "json"
    synthetic_data_path: str = "../data/synthetic"
    ai_provider: str = "local"
    ai_provider_allow_fallback: bool = True
    use_azure_openai: bool = False
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_chat_deployment: str = "gpt-4o-mini"
    azure_openai_reasoning_deployment: str = ""
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_request_timeout_seconds: int = 60
    azure_openai_max_retries: int = 3
    azure_openai_temperature: float = 0.2
    azure_openai_max_tokens: int = 2000
    use_azure_ai_foundry_agent_service: bool = False
    azure_ai_foundry_project_endpoint: str = ""
    azure_ai_foundry_agent_id: str = ""
    azure_ai_foundry_connection_name: str = ""
    azure_ai_foundry_thread_id: str = ""
    llm_enable_json_mode: bool = True
    llm_enable_streaming: bool = False
    llm_log_prompts: bool = False
    llm_log_responses: bool = False
    ai_safety_require_human_review: bool = True
    ai_safety_require_citations: bool = True
    ai_safety_max_recommendation_confidence: str = "HIGH"
    auth_mode: str = "local"
    entra_tenant_id: str = ""
    entra_client_id: str = ""
    entra_api_audience: str = ""
    entra_authority: str = ""
    entra_allow_default_role: bool = False
    azure_search_endpoint: str = ""
    azure_ai_search_endpoint: str = ""
    observability_enabled: bool = True
    observability_mode: str = "local"
    applicationinsights_connection_string: str = ""
    applicationinsights_instrumentation_key: str = ""
    telemetry_service_name: str = "fraud-investigation-platform"
    telemetry_environment: str = "local"
    telemetry_sample_rate: float = 1.0
    telemetry_enable_api: bool = True
    telemetry_enable_agent: bool = True
    telemetry_enable_rag: bool = True
    telemetry_enable_llm: bool = True
    telemetry_enable_business: bool = True
    telemetry_enable_security: bool = True
    telemetry_log_prompts: bool = False
    telemetry_log_responses: bool = False
    telemetry_log_pii: bool = False
    token_cost_input_per_1k: float = 0.0
    token_cost_output_per_1k: float = 0.0
    currency: str = "USD"
    cost_monitoring_enabled: bool = True
    cost_monitoring_mode: str = "local"
    cost_local_store_path: str = "data/synthetic/cost_records.json"
    default_input_token_cost_per_1k: float = 0.0
    default_output_token_cost_per_1k: float = 0.0
    azure_openai_gpt4o_mini_input_cost_per_1k: float = 0.0
    azure_openai_gpt4o_mini_output_cost_per_1k: float = 0.0
    azure_openai_gpt4o_input_cost_per_1k: float = 0.0
    azure_openai_gpt4o_output_cost_per_1k: float = 0.0
    azure_openai_embedding_input_cost_per_1k: float = 0.0
    cost_daily_budget_limit: float = 50
    cost_monthly_budget_limit: float = 1000
    token_daily_limit: int = 1000000
    token_per_case_warning_threshold: int = 25000
    cost_per_case_warning_threshold: float = 2.0
    cost_anomaly_percent_increase_threshold: float = 50
    cost_anomaly_min_baseline_days: int = 3
    azure_cost_management_enabled: bool = False
    azure_subscription_id: str = ""
    azure_resource_group_name: str = ""
    azure_openai_resource_name: str = ""
    azure_ai_search_resource_name: str = ""
    admin_config_enabled: bool = True
    admin_config_mode: str = "local"
    admin_config_local_store_path: str = "data/synthetic/admin_config.json"
    admin_config_history_store_path: str = "data/synthetic/admin_config_history.json"
    admin_config_allow_runtime_updates: bool = True
    admin_config_allow_reset_to_defaults: bool = True
    admin_config_require_admin_role: bool = True
    feature_enable_agentic_investigation: bool = True
    feature_enable_human_review: bool = True
    feature_enable_override_tracking: bool = True
    feature_enable_cost_dashboard: bool = True
    feature_enable_observability_page: bool = True
    feature_enable_alert_simulation: bool = True
    feature_enable_case_assignment: bool = True
    feature_enable_local_demo_mode: bool = True
    feature_enable_azure_search_rag: bool = False
    feature_enable_azure_openai: bool = False
    config_secret_keys_pattern: str = "KEY,SECRET,TOKEN,PASSWORD,CONNECTION_STRING,WEBHOOK"
    azure_app_configuration_enabled: bool = False
    azure_app_configuration_endpoint: str = ""
    azure_key_vault_enabled: bool = False
    azure_key_vault_uri: str = ""
    alerting_enabled: bool = True
    alerting_mode: str = "local"
    incidents_local_store_path: str = "data/synthetic/incidents.json"
    alerts_local_store_path: str = "data/synthetic/alerts.json"
    alert_high_api_error_rate_threshold_percent: float = 5
    alert_high_api_latency_threshold_ms: float = 3000
    alert_high_agent_failure_count: int = 5
    alert_high_rag_empty_result_count: int = 10
    alert_high_llm_latency_threshold_ms: float = 8000
    alert_high_token_usage_threshold: int = 100000
    alert_high_human_override_rate_percent: float = 40
    alert_policy_citation_accuracy_min_percent: float = 80
    alert_stuck_pending_review_hours: int = 24
    notifications_enabled: bool = False
    notification_mode: str = "local"
    teams_webhook_url: str = ""
    email_smtp_host: str = ""
    email_smtp_port: int = 587
    email_smtp_username: str = ""
    email_smtp_password: str = ""
    alert_email_recipients: str = ""
    incident_auto_create_enabled: bool = True
    incident_auto_assign_default_owner: str = "platform-operations"
    case_assignment_enabled: bool = True
    case_assignment_mode: str = "local"
    assignment_history_store_path: str = "data/synthetic/assignment_history.json"
    default_assignment_team: str = "Fraud Operations"
    default_assignment_priority: str = "MEDIUM"
    sla_low_priority_hours: int = 72
    sla_medium_priority_hours: int = 48
    sla_high_priority_hours: int = 24
    sla_critical_priority_hours: int = 4
    auto_set_sla_on_assignment: bool = True
    allow_self_assignment: bool = True
    allow_analyst_release_own_case: bool = True
    allow_analyst_transfer_request: bool = False
    max_active_cases_per_investigator: int = 20
    workload_high_threshold: int = 15
    workload_critical_threshold: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def get_synthetic_data_path() -> Path:
    configured_path = Path(settings.synthetic_data_path)
    if configured_path.is_absolute():
        return configured_path

    backend_dir = Path(__file__).resolve().parents[1]
    return (backend_dir / configured_path).resolve()
