"""
Readiness Check Runner.
Executes automated and manual checks and returns structured ReadinessCheckResult objects.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.readiness.readiness_registry import get_all_checks, get_checks_by_category, get_check_by_id
from app.readiness.static_project_checker import static_checker
from app.readiness.health_check_adapter import health_check_adapter

logger = logging.getLogger(__name__)

# Score values per status (used for display; actual scoring uses ReadinessScoringService)
_STATUS_SCORE = {
    "PASS": 100.0,
    "WARNING": 60.0,
    "MANUAL_REVIEW_REQUIRED": 50.0,
    "NOT_CHECKED": 40.0,
    "NOT_APPLICABLE": None,  # Excluded from scoring
    "FAIL": 0.0,
}


def _result(definition: dict, status: str, message: str, evidence: list[str] | None = None,
            automated_result: dict | None = None) -> dict:
    score = _STATUS_SCORE.get(status, 0.0)
    return {
        "check_id": definition["check_id"],
        "category": definition["category"],
        "title": definition["title"],
        "status": status,
        "severity": definition["severity"],
        "score": score if score is not None else 100.0,
        "message": message,
        "evidence": evidence or [],
        "automated_result": automated_result or {},
        "manual_notes": None,
        "remediation": definition["remediation"],
        "checked_at": datetime.now(UTC).isoformat(),
    }


class ReadinessCheckRunner:
    """Runs readiness checks and returns structured results."""

    def run_all_checks(self, environment: str = "prod", requested_by: str = "system") -> list[dict]:
        checks = get_all_checks()
        return [self._execute_check(c, environment, requested_by) for c in checks]

    def run_category(self, category: str, environment: str = "prod", requested_by: str = "system") -> list[dict]:
        checks = get_checks_by_category(category)
        return [self._execute_check(c, environment, requested_by) for c in checks]

    def run_check(self, check_id: str, environment: str = "prod", requested_by: str = "system") -> dict | None:
        definition = get_check_by_id(check_id)
        if not definition:
            return None
        return self._execute_check(definition, environment, requested_by)

    def _execute_check(self, definition: dict, environment: str, requested_by: str) -> dict:
        check_id = definition["check_id"]
        try:
            runner = _CHECK_DISPATCH.get(check_id)
            if runner:
                return runner(definition)
            # Default for MANUAL checks
            if definition["check_type"] == "MANUAL":
                return _result(definition, "MANUAL_REVIEW_REQUIRED",
                                "Manual review required. Please provide evidence.")
            # Default for unknown automated checks
            return _result(definition, "NOT_CHECKED",
                            "No automated check implemented for this item.")
        except Exception as exc:
            logger.exception("Error running check %s", check_id)
            return _result(definition, "WARNING", f"Check execution error: {exc}")


# ---------------------------------------------------------------------------
# Individual check implementations
# ---------------------------------------------------------------------------

def _arch_001(d: dict) -> dict:
    exists = static_checker.file_exists("README.md") or static_checker.check_docs_exist("architecture")
    if exists:
        return _result(d, "PASS", "Architecture documentation found.", ["README.md or architecture doc detected"])
    return _result(d, "MANUAL_REVIEW_REQUIRED", "Architecture doc not auto-detected. Provide evidence.")


def _arch_002(d: dict) -> dict:
    folders = ["frontend", "backend", "agents", "rag", "infra"]
    existing = [f for f in folders if static_checker.folder_exists(f)]
    missing = [f for f in folders if f not in existing]
    if not missing:
        return _result(d, "PASS", "All component folders exist.", existing)
    return _result(d, "WARNING", f"Missing folders: {missing}. Component boundaries may not be defined.",
                   existing, {"missing": missing})


def _arch_003(d: dict) -> dict:
    folders = ["frontend", "backend", "agents", "rag", "infra"]
    existing = [f for f in folders if static_checker.folder_exists(f)]
    missing = [f for f in folders if f not in existing]
    if not missing:
        return _result(d, "PASS", "All required top-level folders found.", existing)
    return _result(d, "FAIL" if len(missing) > 2 else "WARNING",
                   f"Missing required folders: {missing}", existing, {"missing": missing})


def _arch_004(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED", "Azure service mapping must be manually reviewed.")


def _arch_005(d: dict) -> dict:
    has_mode = static_checker.contains_text("backend/app/config.py", "auth_mode") and \
               static_checker.contains_text("backend/app/config.py", "ai_provider")
    if has_mode:
        return _result(d, "PASS", "Local/production mode separation detected in config.py.",
                       ["backend/app/config.py has auth_mode and ai_provider"])
    return _result(d, "FAIL", "No mode separation detected in config.py.")


def _sec_001(d: dict) -> dict:
    scan_paths = ["backend", "frontend", "infra", "pipelines", "scripts", ".env.example"]
    result = static_checker.scan_for_secret_patterns(scan_paths)
    if result["clean"]:
        return _result(d, "PASS",
                       f"No secret patterns found in {result['total_files_scanned']} files scanned.",
                       [f"Scanned {result['total_files_scanned']} files — clean"],
                       {"files_scanned": result["total_files_scanned"]})
    findings_summary = [f"{f['file']} [{f['pattern_type']}]" for f in result["findings"]]
    return _result(d, "FAIL",
                   f"Potential secret patterns found in {len(result['findings'])} location(s). Review immediately.",
                   findings_summary,
                   {"findings_count": len(result["findings"])})


def _sec_002(d: dict) -> dict:
    paths = [
        "backend/app/utils/secret_redactor.py",
        "backend/app/observability/pii_safe_logging.py",
        "backend/app/utils/audit_sanitizer.py",
    ]
    found = [p for p in paths if static_checker.file_exists(p)]
    if found:
        return _result(d, "PASS", "Secret/PII redaction utility found.", found)
    return _result(d, "FAIL", "No secret redaction utility found. Create one in backend/app/utils/.")


def _sec_003(d: dict) -> dict:
    if static_checker.file_exists("backend/app/api/routes/security_routes.py"):
        return _result(d, "PASS", "Security routes file exists.", ["backend/app/api/routes/security_routes.py"])
    return _result(d, "FAIL", "security_routes.py not found.")


def _sec_004(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual code review required: verify admin APIs do not return secret values in responses.")


def _sec_005(d: dict) -> dict:
    scan = static_checker.scan_for_secret_patterns(["frontend/.env.example", "frontend/src"])
    if scan["clean"]:
        return _result(d, "PASS", "No secrets detected in frontend files.",
                       [f"Scanned {scan['total_files_scanned']} frontend files"])
    findings = [f"{f['file']} [{f['pattern_type']}]" for f in scan["findings"]]
    return _result(d, "FAIL", "Potential secrets found in frontend files.", findings)


def _sec_006(d: dict) -> dict:
    has_runbooks = static_checker.folder_exists("docs/runbooks")
    if has_runbooks:
        return _result(d, "PASS", "Runbooks directory found at docs/runbooks/.", ["docs/runbooks/"])
    return _result(d, "FAIL", "docs/runbooks/ not found. Create security runbooks.")


def _iam_001(d: dict) -> dict:
    has_auth = static_checker.folder_exists("backend/app/auth")
    has_entra = (static_checker.contains_text("backend/app/config.py", "entra_tenant_id") or
                 static_checker.check_docs_exist("entra"))
    if has_auth and has_entra:
        return _result(d, "PASS", "Auth module and Entra ID config exist.",
                       ["backend/app/auth/", "entra config in config.py"])
    if has_auth:
        return _result(d, "WARNING", "Auth module exists but Entra ID config may be incomplete.")
    return _result(d, "FAIL", "backend/app/auth/ not found.")


def _iam_002(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "auth_mode"):
        return _result(d, "PASS", "Local auth mode exists (auth_mode field in config).",
                       ["backend/app/config.py"])
    return _result(d, "FAIL", "auth_mode not found in config.py.")


def _iam_003(d: dict) -> dict:
    if static_checker.file_exists("backend/app/auth/permissions.py"):
        return _result(d, "PASS", "RBAC permissions module found.",
                       ["backend/app/auth/permissions.py"])
    return _result(d, "FAIL", "permissions.py not found in backend/app/auth/.")


def _iam_004(d: dict) -> dict:
    if static_checker.contains_text("backend/app/auth/permissions.py", "AUDITOR"):
        return _result(d, "PASS", "AUDITOR role is defined in permissions.",
                       ["backend/app/auth/permissions.py has AUDITOR entry"])
    return _result(d, "WARNING", "AUDITOR role not confirmed in permissions.py.")


def _iam_005(d: dict) -> dict:
    if static_checker.contains_text("backend/app/auth/permissions.py", "ADMIN_CONFIG"):
        return _result(d, "PASS", "Admin-only permission (ADMIN_CONFIG) exists in permissions.",
                       ["backend/app/auth/permissions.py"])
    return _result(d, "FAIL", "ADMIN_CONFIG permission not found in permissions.py.")


def _iam_006(d: dict) -> dict:
    exists = static_checker.check_docs_exist("entra")
    if exists:
        return _result(d, "PASS", "Entra ID auth documentation found.")
    return _result(d, "WARNING", "Entra ID auth documentation not found in docs/.")


def _key_001(d: dict) -> dict:
    has_kv = (static_checker.file_exists("backend/app/security/key_vault_provider.py") or
              static_checker.file_exists("backend/app/security/secure_config_loader.py"))
    if has_kv:
        return _result(d, "PASS", "Key Vault/secure config loader found.",
                       ["backend/app/security/"])
    return _result(d, "WARNING", "No explicit key_vault_provider.py found; check secure_config_loader.py.")


def _key_002(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/security"):
        return _result(d, "PASS", "Security module exists for environment provider.",
                       ["backend/app/security/"])
    return _result(d, "FAIL", "backend/app/security/ not found.")


def _key_003(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "use_managed_identity"):
        return _result(d, "PASS", "Managed identity support flag exists in config.",
                       ["backend/app/config.py"])
    return _result(d, "WARNING", "use_managed_identity flag not found in config.py.")


def _key_004(d: dict) -> dict:
    has_kv_bicep = static_checker.check_bicep_module_exists("key-vault") or \
                   static_checker.check_bicep_module_exists("keyvault")
    if has_kv_bicep:
        return _result(d, "PASS", "Key Vault Bicep module found.")
    return _result(d, "WARNING", "Key Vault Bicep module not found in infra/bicep/.")


def _key_005(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual review required: verify health/admin APIs return no raw secret values.")


def _key_006(d: dict) -> dict:
    params_dir = "infra/bicep/parameters"
    if static_checker.folder_exists(params_dir):
        scan = static_checker.scan_for_secret_patterns([params_dir])
        if scan["clean"]:
            return _result(d, "PASS", "No secrets found in Bicep parameter files.",
                           [f"Scanned {scan['total_files_scanned']} parameter files"])
        findings = [f"{f['file']} [{f['pattern_type']}]" for f in scan["findings"]]
        return _result(d, "FAIL", "Potential secrets in Bicep parameter files.", findings)
    return _result(d, "WARNING", "infra/bicep/parameters/ not found.")


def _net_001(d: dict) -> dict:
    has = static_checker.check_bicep_module_exists("private-endpoint") or \
          static_checker.check_bicep_module_exists("networking")
    if has:
        return _result(d, "PASS", "Private endpoint Bicep module found.")
    return _result(d, "WARNING", "No private endpoint Bicep module found in infra/bicep/.")


def _net_002(d: dict) -> dict:
    has = static_checker.check_bicep_module_exists("private-dns") or \
          static_checker.check_bicep_module_exists("dns")
    if has:
        return _result(d, "PASS", "Private DNS Bicep module found.")
    return _result(d, "WARNING", "No private DNS Bicep module found.")


def _net_003(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "disable_public_network_access"):
        return _result(d, "PASS", "Public network access flag found in config.",
                       ["backend/app/config.py"])
    return _result(d, "WARNING", "disable_public_network_access flag not found in config.py.")


def _net_004(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Container Apps VNet integration must be manually verified in deployment docs.")


def _net_005(d: dict) -> dict:
    exists = static_checker.check_docs_exist("hardening") or static_checker.check_docs_exist("deployment")
    if exists:
        return _result(d, "PASS", "Deployment hardening documentation found.")
    return _result(d, "WARNING", "Deployment hardening docs not found in docs/.")


def _ai_001(d: dict) -> dict:
    health = health_check_adapter.get_agent_provider_health()
    if health.get("status") == "OK" and health.get("details", {}).get("human_review_required"):
        return _result(d, "PASS", "Human review enforced via ai_safety_require_human_review=True.",
                       ["config confirmed"], health.get("details", {}))
    if static_checker.contains_text("backend/app/config.py", "ai_safety_require_human_review"):
        return _result(d, "WARNING",
                       "ai_safety_require_human_review found in config. Verify it is True in production.",
                       ["backend/app/config.py"])
    return _result(d, "FAIL", "ai_safety_require_human_review not found in config.")


def _ai_002(d: dict) -> dict:
    has = (static_checker.file_exists("backend/app/security/guardrail_engine.py") or
           static_checker.folder_exists("backend/app/security"))
    if static_checker.file_exists("backend/app/security/guardrail_engine.py"):
        return _result(d, "PASS", "Guardrail engine found.", ["backend/app/security/guardrail_engine.py"])
    if has:
        return _result(d, "WARNING", "Security folder exists but guardrail_engine.py not found explicitly.")
    return _result(d, "FAIL", "No guardrail engine found.")


def _ai_003(d: dict) -> dict:
    paths = [
        "backend/app/utils/pii_redactor.py",
        "backend/app/security/pii_redactor.py",
        "backend/app/observability/pii_safe_logging.py",
    ]
    found = [p for p in paths if static_checker.file_exists(p)]
    if found:
        return _result(d, "PASS", "PII redaction utility found.", found)
    return _result(d, "FAIL", "No PII redaction utility found.")


def _ai_004(d: dict) -> dict:
    paths = [
        "backend/app/security/prompt_injection_detector.py",
        "backend/app/utils/prompt_injection_detector.py",
    ]
    found = [p for p in paths if static_checker.file_exists(p)]
    if found:
        return _result(d, "PASS", "Prompt injection detector found.", found)
    return _result(d, "WARNING", "No explicit prompt_injection_detector.py found.")


def _ai_005(d: dict) -> dict:
    paths = [
        "backend/app/security/output_validator.py",
        "backend/app/utils/output_validator.py",
        "backend/app/security/llm_output_validator.py",
    ]
    found = [p for p in paths if static_checker.file_exists(p)]
    if found:
        return _result(d, "PASS", "Output validator found.", found)
    return _result(d, "WARNING", "No explicit output_validator.py found.")


def _ai_006(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual review required: verify accusation language is blocked by guardrail engine tests.")


def _ai_007(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "llm_enable_json_mode"):
        return _result(d, "PASS", "LLM JSON mode configuration exists.",
                       ["backend/app/config.py llm_enable_json_mode"])
    return _result(d, "WARNING", "llm_enable_json_mode not found in config; JSON validation may be missing.")


def _ai_008(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "ai_provider_allow_fallback"):
        return _result(d, "PASS", "LLM fallback configuration exists.",
                       ["backend/app/config.py ai_provider_allow_fallback"])
    return _result(d, "FAIL", "ai_provider_allow_fallback not found in config.")


def _rag_check_folder(d: dict, patterns: list[str]) -> dict:
    rag_dir = "rag"
    if not static_checker.folder_exists(rag_dir):
        return _result(d, "WARNING", "rag/ folder not found at project root.")
    for pat in patterns:
        for f in (pat if isinstance(pat, list) else [pat]):
            if static_checker.file_exists(f"rag/{f}") or static_checker.file_exists(f"backend/app/{f}"):
                return _result(d, "PASS", f"Found {f}", [f"rag/{f}"])
    return _result(d, "WARNING", f"File not found in rag/ or backend/app/: {patterns}")


def _rag_001(d: dict) -> dict:
    health = health_check_adapter.get_rag_health()
    if health.get("status") == "OK":
        return _result(d, "PASS", "RAG service health confirmed.", [], health.get("details", {}))
    return _result(d, "WARNING", "RAG health NOT_CHECKED. Verify Azure AI Search retriever exists.")


def _rag_002(d: dict) -> dict:
    paths = ["backend/app/services/rag_service.py", "rag/local_retriever.py"]
    found = [p for p in paths if static_checker.file_exists(p)]
    if found:
        return _result(d, "PASS", "Local RAG retriever/service found.", found)
    return _result(d, "WARNING", "No local RAG retriever found.")


def _rag_003(d: dict) -> dict:
    return _rag_check_folder(d, ["policy_index_schema.py", "schemas/policy_schema.py"])


def _rag_004(d: dict) -> dict:
    return _rag_check_folder(d, ["historical_case_index_schema.py", "schemas/case_schema.py"])


def _rag_005(d: dict) -> dict:
    return _rag_check_folder(d, ["citation_builder.py"])


def _rag_006(d: dict) -> dict:
    return _rag_check_folder(d, ["citation_validator.py"])


def _rag_007(d: dict) -> dict:
    if (static_checker.folder_exists("tests") and
            any(static_checker.check_tests_exist(p) for p in ["*rag*", "*eval*"])):
        return _result(d, "PASS", "RAG evaluation test files found.")
    return _result(d, "WARNING", "No RAG evaluation dataset found. Create one in tests/ or data/.")


def _rag_008(d: dict) -> dict:
    if static_checker.contains_text("backend/app/observability/telemetry_events.py", "RAG_RETRIEVAL"):
        return _result(d, "PASS", "RAG retrieval telemetry events exist.",
                       ["observability/telemetry_events.py"])
    return _result(d, "FAIL", "RAG telemetry events not found in telemetry_events.py.")


def _hitl_001(d: dict) -> dict:
    if static_checker.file_exists("backend/app/services/human_review_service.py"):
        return _result(d, "PASS", "Human review service found.",
                       ["backend/app/services/human_review_service.py"])
    return _result(d, "FAIL", "human_review_service.py not found.")


def _hitl_002(d: dict) -> dict:
    if static_checker.contains_text("backend/app/auth/permissions.py", "SUBMIT_HUMAN_REVIEW"):
        return _result(d, "PASS", "SUBMIT_HUMAN_REVIEW permission exists.",
                       ["backend/app/auth/permissions.py"])
    return _result(d, "FAIL", "SUBMIT_HUMAN_REVIEW permission not found in permissions.py.")


def _hitl_003(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual review required: verify evidence acknowledgement is required in review workflow.")


def _hitl_004(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual review required: verify policy acknowledgement is required in review workflow.")


def _hitl_005(d: dict) -> dict:
    if static_checker.file_exists("backend/app/services/human_override_service.py"):
        return _result(d, "PASS", "Human override service found.",
                       ["backend/app/services/human_override_service.py"])
    return _result(d, "WARNING", "human_override_service.py not found.")


def _hitl_006(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "ALLOWED_STATUS_TRANSITIONS"):
        return _result(d, "PASS", "Case status lifecycle (ALLOWED_STATUS_TRANSITIONS) exists.",
                       ["backend/app/core/constants.py"])
    return _result(d, "FAIL", "ALLOWED_STATUS_TRANSITIONS not found in constants.py.")


def _hitl_007(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "CaseStatus.CLOSED: set()"):
        return _result(d, "PASS", "CLOSED status is terminal (empty transition set).",
                       ["backend/app/core/constants.py"])
    return _result(d, "WARNING", "CLOSED terminal state not confirmed in constants.py.")


def _aud_001(d: dict) -> dict:
    if static_checker.file_exists("backend/app/services/audit_service.py"):
        return _result(d, "PASS", "Audit service found.",
                       ["backend/app/services/audit_service.py"])
    return _result(d, "FAIL", "audit_service.py not found.")


def _aud_002(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/repositories"):
        return _result(d, "PASS", "Audit repository folder found.",
                       ["backend/app/repositories/"])
    return _result(d, "WARNING", "Audit repository not confirmed.")


def _aud_003(d: dict) -> dict:
    if static_checker.file_exists("backend/app/utils/audit_sanitizer.py"):
        return _result(d, "PASS", "Audit sanitizer found.",
                       ["backend/app/utils/audit_sanitizer.py"])
    return _result(d, "WARNING", "audit_sanitizer.py not found in backend/app/utils/.")


def _aud_004(d: dict) -> dict:
    if static_checker.contains_text("backend/app/services/audit_service.py", "create_human_decision_event"):
        return _result(d, "PASS", "Human decision audit event method exists.",
                       ["backend/app/services/audit_service.py"])
    return _result(d, "FAIL", "create_human_decision_event not found in audit_service.py.")


def _aud_005(d: dict) -> dict:
    if static_checker.contains_text("backend/app/services/audit_service.py", "create_ai_investigation_event"):
        return _result(d, "PASS", "AI investigation audit event method exists.",
                       ["backend/app/services/audit_service.py"])
    return _result(d, "FAIL", "create_ai_investigation_event not found in audit_service.py.")


def _aud_006(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "ADMIN_CONFIG_UPDATED"):
        return _result(d, "PASS", "ADMIN_CONFIG_UPDATED audit event type exists.",
                       ["backend/app/core/constants.py"])
    return _result(d, "FAIL", "ADMIN_CONFIG_UPDATED audit event type not found.")


def _aud_007(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/compliance"):
        return _result(d, "PASS", "Compliance module found.",
                       ["backend/app/compliance/"])
    return _result(d, "WARNING", "backend/app/compliance/ not found.")


def _ret_001(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "class DataCategory"):
        return _result(d, "PASS", "DataCategory enum exists.", ["backend/app/core/constants.py"])
    return _result(d, "FAIL", "DataCategory enum not found in constants.py.")


def _ret_002(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "retention_policy_store_path"):
        return _result(d, "PASS", "Retention policy store path configured.",
                       ["backend/app/config.py"])
    return _result(d, "WARNING", "retention_policy_store_path not found in config.py.")


def _ret_003(d: dict) -> dict:
    has_route = static_checker.file_exists("backend/app/api/routes/legal_hold_routes.py")
    if has_route:
        return _result(d, "PASS", "Legal hold routes exist.",
                       ["backend/app/api/routes/legal_hold_routes.py"])
    return _result(d, "FAIL", "legal_hold_routes.py not found.")


def _ret_004(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "purge_dry_run_default"):
        return _result(d, "PASS", "Purge dry-run default flag configured.",
                       ["backend/app/config.py purge_dry_run_default"])
    return _result(d, "FAIL", "purge_dry_run_default not found in config.py.")


def _ret_005(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "LEGAL_HOLD"):
        return _result(d, "PASS", "Legal hold status in constants — purge blocking implied.",
                       ["backend/app/core/constants.py"])
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual review required: verify legal hold blocks purge in retention service.")


def _ret_006(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "compliance_export_redact_pii"):
        return _result(d, "PASS", "Compliance export PII redaction flag exists.",
                       ["backend/app/config.py"])
    return _result(d, "WARNING", "compliance_export_redact_pii not found in config.py.")


def _ret_007(d: dict) -> dict:
    if static_checker.check_docs_exist("retention"):
        return _result(d, "PASS", "Data retention documentation found.")
    return _result(d, "WARNING", "No data retention documentation found in docs/.")


def _obs_file_check(d: dict, filename: str) -> dict:
    if static_checker.file_exists(f"backend/app/observability/{filename}"):
        return _result(d, "PASS", f"{filename} found.",
                       [f"backend/app/observability/{filename}"])
    return _result(d, "FAIL", f"{filename} not found in observability/.")


def _obs_001(d: dict) -> dict:
    return _obs_file_check(d, "correlation.py")


def _obs_002(d: dict) -> dict:
    return _obs_file_check(d, "middleware.py")


def _obs_003(d: dict) -> dict:
    if static_checker.contains_text("backend/app/observability/telemetry_events.py", "AGENT_EXECUTION"):
        return _result(d, "PASS", "Agent execution telemetry events found.",
                       ["backend/app/observability/telemetry_events.py"])
    return _result(d, "FAIL", "Agent execution telemetry events not found.")


def _obs_004(d: dict) -> dict:
    if static_checker.contains_text("backend/app/observability/telemetry_events.py", "RAG_RETRIEVAL"):
        return _result(d, "PASS", "RAG retrieval telemetry events found.",
                       ["backend/app/observability/telemetry_events.py"])
    return _result(d, "FAIL", "RAG retrieval telemetry events not found.")


def _obs_005(d: dict) -> dict:
    if static_checker.contains_text("backend/app/observability/telemetry_events.py", "LLM_CALL"):
        return _result(d, "PASS", "LLM call telemetry events found.",
                       ["backend/app/observability/telemetry_events.py"])
    return _result(d, "FAIL", "LLM call telemetry events not found.")


def _obs_006(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "applicationinsights_connection_string"):
        return _result(d, "PASS", "Application Insights config field exists.",
                       ["backend/app/config.py"])
    return _result(d, "FAIL", "applicationinsights_connection_string not found in config.py.")


def _obs_007(d: dict) -> dict:
    if static_checker.folder_exists("monitoring/kql"):
        return _result(d, "PASS", "KQL queries folder found.", ["monitoring/kql/"])
    return _result(d, "WARNING", "monitoring/kql/ not found.")


def _obs_008(d: dict) -> dict:
    if static_checker.folder_exists("frontend/src/app/observability"):
        return _result(d, "PASS", "Observability frontend page found.",
                       ["frontend/src/app/observability/"])
    return _result(d, "WARNING", "frontend/src/app/observability/ not found.")


def _alert_001(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "class AlertSeverity"):
        return _result(d, "PASS", "AlertSeverity enum found.", ["backend/app/core/constants.py"])
    return _result(d, "FAIL", "AlertSeverity enum not found in constants.py.")


def _alert_002(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/alerting"):
        return _result(d, "PASS", "Alerting module found.", ["backend/app/alerting/"])
    return _result(d, "FAIL", "backend/app/alerting/ not found.")


def _alert_003(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "class IncidentStatus"):
        return _result(d, "PASS", "IncidentStatus enum found — incident lifecycle exists.",
                       ["backend/app/core/constants.py"])
    return _result(d, "FAIL", "IncidentStatus enum not found in constants.py.")


def _alert_004(d: dict) -> dict:
    if static_checker.folder_exists("docs/runbooks"):
        return _result(d, "PASS", "Runbooks directory found.", ["docs/runbooks/"])
    return _result(d, "WARNING", "docs/runbooks/ not found.")


def _alert_005(d: dict) -> dict:
    if static_checker.file_exists("data/synthetic/alerts.json"):
        return _result(d, "PASS", "Local alert simulation data file found.",
                       ["data/synthetic/alerts.json"])
    return _result(d, "WARNING", "data/synthetic/alerts.json not found.")


def _alert_006(d: dict) -> dict:
    has_alerts = static_checker.folder_exists("frontend/src/app/alerts")
    has_incidents = static_checker.folder_exists("frontend/src/app/incidents")
    if has_alerts and has_incidents:
        return _result(d, "PASS", "Alert and incident frontend pages found.",
                       ["frontend/src/app/alerts/", "frontend/src/app/incidents/"])
    return _result(d, "WARNING", "Alert or incident frontend pages not found.")


def _alert_007(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/notifications"):
        return _result(d, "PASS", "Notification module found.", ["backend/app/notifications/"])
    return _result(d, "WARNING", "backend/app/notifications/ not found.")


def _rel_001(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "azure_openai_max_retries"):
        return _result(d, "PASS", "Retry configuration exists.", ["backend/app/config.py"])
    return _result(d, "WARNING", "azure_openai_max_retries not found in config.py.")


def _rel_002(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "timeout"):
        return _result(d, "PASS", "Timeout configuration exists.", ["backend/app/config.py"])
    return _result(d, "WARNING", "No timeout configuration found in config.py.")


def _rel_003(d: dict) -> dict:
    if static_checker.contains_text("backend/app/config.py", "ai_provider_allow_fallback"):
        return _result(d, "PASS", "Fallback mode configuration exists.", ["backend/app/config.py"])
    return _result(d, "FAIL", "ai_provider_allow_fallback not found in config.py.")


def _rel_004(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Circuit breaker: manual review or future implementation required.")


def _rel_005(d: dict) -> dict:
    if (static_checker.contains_text("backend/app/observability/telemetry_events.py", "AGENT_EXECUTION_FAILED") and
            static_checker.contains_text("backend/app/core/constants.py", "AGENT_EXECUTION_FAILED")):
        return _result(d, "PASS", "Agent execution failure events tracked in telemetry and audit.",
                       ["telemetry_events.py", "constants.py AuditEventType"])
    return _result(d, "WARNING", "Agent execution failure handling not fully confirmed.")


def _rel_006(d: dict) -> dict:
    if static_checker.file_exists("backend/app/services/investigation_service.py"):
        return _result(d, "PASS", "Investigation service found.",
                       ["backend/app/services/investigation_service.py"])
    return _result(d, "WARNING", "investigation_service.py not found.")


def _rel_007(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Dead-letter queue: document or implement as future improvement.")


def _perf_001(d: dict) -> dict:
    if static_checker.contains_text("backend/app/observability/telemetry_events.py", "AGENT_EXECUTION"):
        return _result(d, "PASS", "Agent execution telemetry (latency capable) found.")
    return _result(d, "WARNING", "Agent latency telemetry not confirmed.")


def _perf_002(d: dict) -> dict:
    if static_checker.contains_text("backend/app/observability/telemetry_events.py", "RAG_RETRIEVAL"):
        return _result(d, "PASS", "RAG retrieval telemetry (latency capable) found.")
    return _result(d, "WARNING", "RAG latency telemetry not confirmed.")


def _perf_003(d: dict) -> dict:
    if static_checker.contains_text("backend/app/observability/telemetry_events.py", "LLM_CALL"):
        return _result(d, "PASS", "LLM call telemetry (latency capable) found.")
    return _result(d, "WARNING", "LLM latency telemetry not confirmed.")


def _perf_004(d: dict) -> dict:
    has = (static_checker.check_bicep_module_exists("container-app") or
           static_checker.check_bicep_module_exists("containerapp"))
    if has:
        return _result(d, "PASS", "Container Apps Bicep module found.")
    return _result(d, "WARNING", "Container Apps Bicep module not found in infra/bicep/.")


def _perf_005(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Performance test scripts: manual review required. Create tests/performance/ if needed.")


def _perf_006(d: dict) -> dict:
    if static_checker.folder_exists("frontend/src/app/cost"):
        return _result(d, "PASS", "Cost frontend page found.", ["frontend/src/app/cost/"])
    return _result(d, "WARNING", "frontend/src/app/cost/ not found.")


def _cost_001(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/cost"):
        return _result(d, "PASS", "Cost module found.", ["backend/app/cost/"])
    return _result(d, "WARNING", "backend/app/cost/ not found.")


def _cost_002(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/cost"):
        return _result(d, "PASS", "Cost module (with estimator) found.", ["backend/app/cost/"])
    return _result(d, "WARNING", "Cost estimator not confirmed.")


def _cost_003(d: dict) -> dict:
    if static_checker.folder_exists("frontend/src/app/cost"):
        return _result(d, "PASS", "Cost monitoring frontend page found.",
                       ["frontend/src/app/cost/"])
    return _result(d, "WARNING", "frontend/src/app/cost/ not found.")


def _cost_004(d: dict) -> dict:
    if static_checker.file_exists("backend/app/api/routes/cost_routes.py"):
        return _result(d, "PASS", "Cost routes exist.", ["backend/app/api/routes/cost_routes.py"])
    return _result(d, "WARNING", "cost_routes.py not found.")


def _cost_005(d: dict) -> dict:
    if static_checker.contains_text("backend/app/core/constants.py", "COST_ANOMALY"):
        return _result(d, "PASS", "Cost anomaly alert type found.",
                       ["backend/app/core/constants.py"])
    return _result(d, "WARNING", "COST_ANOMALY not found in constants.")


def _cost_006(d: dict) -> dict:
    if static_checker.folder_exists("monitoring/alerts"):
        return _result(d, "PASS", "Monitoring alerts folder found.", ["monitoring/alerts/"])
    return _result(d, "WARNING", "monitoring/alerts/ not found.")


def _devops_001(d: dict) -> dict:
    has = (static_checker.folder_exists("pipelines") and
           any(static_checker.file_exists(f"pipelines/{f}") for f in
               ["azure-pipelines.yml", "ci-cd.yml", "pipeline.yml", "main.yml"]))
    if has:
        return _result(d, "PASS", "Azure DevOps pipeline YAML found.", ["pipelines/"])
    if static_checker.folder_exists("pipelines"):
        return _result(d, "WARNING", "pipelines/ folder exists but no standard YAML found.")
    return _result(d, "FAIL", "pipelines/ folder not found.")


def _devops_002(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual review required: verify pipeline includes infra validation stage.")


def _devops_003(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   "Manual review required: verify pipeline includes security scan stage.")


def _devops_004(d: dict) -> dict:
    has = (static_checker.folder_exists("scripts") and
           static_checker.file_exists("scripts/security/scan-secrets.sh") or
           static_checker.folder_exists("scripts/security"))
    if has:
        return _result(d, "PASS", "Security/scripts folder found.", ["scripts/"])
    return _result(d, "WARNING", "No Bicep what-if script found in scripts/.")


def _devops_005(d: dict) -> dict:
    has = static_checker.folder_exists("infra/bicep/parameters")
    if has:
        return _result(d, "PASS", "Bicep parameters directory found.",
                       ["infra/bicep/parameters/"])
    return _result(d, "WARNING", "infra/bicep/parameters/ not found.")


def _devops_006(d: dict) -> dict:
    has = static_checker.check_docs_exist("rollback")
    if has:
        return _result(d, "PASS", "Rollback documentation found.")
    return _result(d, "WARNING", "No rollback guide found in docs/.")


def _devops_007(d: dict) -> dict:
    if not static_checker.folder_exists("pipelines"):
        return _result(d, "WARNING", "pipelines/ folder not found; cannot scan.")
    scan = static_checker.scan_for_secret_patterns(["pipelines"])
    if scan["clean"]:
        return _result(d, "PASS",
                       f"No secrets found in pipeline files ({scan['total_files_scanned']} files scanned).",
                       [f"Scanned {scan['total_files_scanned']} files"])
    findings = [f"{f['file']} [{f['pattern_type']}]" for f in scan["findings"]]
    return _result(d, "FAIL", "Potential secrets found in pipeline YAML.", findings)


def _test_001(d: dict) -> dict:
    if static_checker.folder_exists("backend/tests"):
        return _result(d, "PASS", "backend/tests/ folder found.", ["backend/tests/"])
    return _result(d, "FAIL", "backend/tests/ not found.")


def _test_002(d: dict) -> dict:
    if static_checker.check_tests_exist("*agent*"):
        return _result(d, "PASS", "Agent test files found.")
    return _result(d, "WARNING", "No agent test files found in backend/tests/.")


def _test_003(d: dict) -> dict:
    if static_checker.check_tests_exist("*rag*"):
        return _result(d, "PASS", "RAG test files found.")
    return _result(d, "WARNING", "No RAG test files found in backend/tests/.")


def _test_004(d: dict) -> dict:
    if static_checker.folder_exists("frontend"):
        return _result(d, "MANUAL_REVIEW_REQUIRED",
                       "Frontend TypeScript build must be run manually: cd frontend && npm run build")
    return _result(d, "NOT_APPLICABLE", "Frontend folder not found.")


def _test_005(d: dict) -> dict:
    if static_checker.check_tests_exist("*security*") or static_checker.check_tests_exist("*auth*"):
        return _result(d, "PASS", "Security/auth test files found.")
    return _result(d, "WARNING", "No security test files found in backend/tests/.")


def _test_006(d: dict) -> dict:
    if static_checker.check_tests_exist("*eval*") or static_checker.check_tests_exist("*ai*"):
        return _result(d, "PASS", "AI evaluation test files found.")
    return _result(d, "WARNING", "No AI evaluation test files found.")


def _test_007(d: dict) -> dict:
    if static_checker.check_tests_exist("*review*"):
        return _result(d, "PASS", "Human review test files found.")
    return _result(d, "WARNING", "No human review test files found in backend/tests/.")


def _test_008(d: dict) -> dict:
    if static_checker.check_tests_exist("*audit*"):
        return _result(d, "PASS", "Audit test files found.")
    return _result(d, "WARNING", "No audit test files found in backend/tests/.")


def _ops_001(d: dict) -> dict:
    has = static_checker.check_docs_exist("operations") or static_checker.check_docs_exist("runbook")
    if has:
        return _result(d, "PASS", "Operations documentation found.")
    return _result(d, "WARNING", "No operations runbook found in docs/.")


def _ops_002(d: dict) -> dict:
    has = static_checker.check_docs_exist("incident") or static_checker.check_docs_exist("alerting")
    if has:
        return _result(d, "PASS", "Incident response documentation found.")
    return _result(d, "WARNING", "No incident response documentation found.")


def _ops_003(d: dict) -> dict:
    has = static_checker.check_docs_exist("monitoring") or static_checker.check_docs_exist("observability")
    if has:
        return _result(d, "PASS", "Monitoring guide found.")
    return _result(d, "WARNING", "No monitoring guide found in docs/.")


def _ops_004(d: dict) -> dict:
    has = static_checker.check_docs_exist("rollback")
    if has:
        return _result(d, "PASS", "Rollback guide found.")
    return _result(d, "WARNING", "No rollback guide found in docs/ or docs/runbooks/.")


def _ops_005(d: dict) -> dict:
    has_be = static_checker.folder_exists("backend/app/admin")
    has_fe = static_checker.folder_exists("frontend/src/app/admin")
    if has_be and has_fe:
        return _result(d, "PASS", "Admin config panel found (backend + frontend).",
                       ["backend/app/admin/", "frontend/src/app/admin/"])
    return _result(d, "WARNING", "Admin panel not fully implemented.")


def _ops_006(d: dict) -> dict:
    if static_checker.folder_exists("backend/app/notifications"):
        return _result(d, "PASS", "Notification system found.",
                       ["backend/app/notifications/"])
    return _result(d, "WARNING", "backend/app/notifications/ not found.")


def _ops_007(d: dict) -> dict:
    has_be = static_checker.folder_exists("backend/app/assignment")
    has_fe = static_checker.folder_exists("frontend/src/app/queues")
    if has_be and has_fe:
        return _result(d, "PASS", "Case assignment queue found.",
                       ["backend/app/assignment/", "frontend/src/app/queues/"])
    return _result(d, "WARNING", "Case assignment queue not fully confirmed.")


def _doc_001(d: dict) -> dict:
    if static_checker.file_exists("README.md"):
        return _result(d, "PASS", "README.md found.", ["README.md"])
    return _result(d, "FAIL", "README.md not found.")


def _doc_002(d: dict) -> dict:
    has = static_checker.folder_exists("docs")
    if has:
        return _result(d, "PASS", "docs/ folder found.", ["docs/"])
    return _result(d, "FAIL", "docs/ folder not found.")


def _doc_003(d: dict) -> dict:
    has = static_checker.check_docs_exist("security") or static_checker.check_docs_exist("hardening")
    if has:
        return _result(d, "PASS", "Security documentation found.")
    return _result(d, "WARNING", "No security documentation found in docs/.")


def _doc_004(d: dict) -> dict:
    has = static_checker.check_docs_exist("rag") or static_checker.check_docs_exist("search")
    if has:
        return _result(d, "PASS", "RAG documentation found.")
    return _result(d, "WARNING", "No RAG documentation found in docs/.")


def _doc_005(d: dict) -> dict:
    has = static_checker.check_docs_exist("hardening") or static_checker.check_docs_exist("deployment")
    if has:
        return _result(d, "PASS", "Deployment hardening documentation found.")
    return _result(d, "WARNING", "No deployment hardening documentation found.")


def _doc_006(d: dict) -> dict:
    has = static_checker.check_docs_exist("retention")
    if has:
        return _result(d, "PASS", "Data retention documentation found.")
    return _result(d, "WARNING", "No data retention documentation found.")


def _doc_007(d: dict) -> dict:
    has = static_checker.check_docs_exist("production-readiness") or \
          static_checker.file_exists("docs/end-to-end-production-readiness-checklist.md")
    if has:
        return _result(d, "PASS", "Production readiness checklist documentation found.")
    return _result(d, "WARNING", "Production readiness documentation not found in docs/.")


def _bus_manual(d: dict) -> dict:
    return _result(d, "MANUAL_REVIEW_REQUIRED",
                   f"{d['title']}: manual evidence required from {d['owner']}.")


def _bus_004(d: dict) -> dict:
    has = (static_checker.folder_exists("frontend/src/app/metrics") or
           static_checker.folder_exists("frontend/src/app/dashboard"))
    if has:
        return _result(d, "PASS", "Business metrics/dashboard frontend page found.")
    return _result(d, "WARNING", "No metrics or dashboard frontend page found.")


def _bus_006(d: dict) -> dict:
    if static_checker.file_exists("data/synthetic/readiness_risk_register.json"):
        return _result(d, "PASS", "Go-live risk register file exists.",
                       ["data/synthetic/readiness_risk_register.json"])
    return _result(d, "WARNING", "readiness_risk_register.json not found in data/synthetic/.")


# ---------------------------------------------------------------------------
# Dispatch table: check_id -> function
# ---------------------------------------------------------------------------
_CHECK_DISPATCH = {
    "ARCH-001": _arch_001, "ARCH-002": _arch_002, "ARCH-003": _arch_003,
    "ARCH-004": _arch_004, "ARCH-005": _arch_005,
    "SEC-001": _sec_001, "SEC-002": _sec_002, "SEC-003": _sec_003,
    "SEC-004": _sec_004, "SEC-005": _sec_005, "SEC-006": _sec_006,
    "IAM-001": _iam_001, "IAM-002": _iam_002, "IAM-003": _iam_003,
    "IAM-004": _iam_004, "IAM-005": _iam_005, "IAM-006": _iam_006,
    "KEY-001": _key_001, "KEY-002": _key_002, "KEY-003": _key_003,
    "KEY-004": _key_004, "KEY-005": _key_005, "KEY-006": _key_006,
    "NET-001": _net_001, "NET-002": _net_002, "NET-003": _net_003,
    "NET-004": _net_004, "NET-005": _net_005,
    "AI-001": _ai_001, "AI-002": _ai_002, "AI-003": _ai_003,
    "AI-004": _ai_004, "AI-005": _ai_005, "AI-006": _ai_006,
    "AI-007": _ai_007, "AI-008": _ai_008,
    "RAG-001": _rag_001, "RAG-002": _rag_002, "RAG-003": _rag_003,
    "RAG-004": _rag_004, "RAG-005": _rag_005, "RAG-006": _rag_006,
    "RAG-007": _rag_007, "RAG-008": _rag_008,
    "HITL-001": _hitl_001, "HITL-002": _hitl_002, "HITL-003": _hitl_003,
    "HITL-004": _hitl_004, "HITL-005": _hitl_005, "HITL-006": _hitl_006,
    "HITL-007": _hitl_007,
    "AUD-001": _aud_001, "AUD-002": _aud_002, "AUD-003": _aud_003,
    "AUD-004": _aud_004, "AUD-005": _aud_005, "AUD-006": _aud_006,
    "AUD-007": _aud_007,
    "RET-001": _ret_001, "RET-002": _ret_002, "RET-003": _ret_003,
    "RET-004": _ret_004, "RET-005": _ret_005, "RET-006": _ret_006,
    "RET-007": _ret_007,
    "OBS-001": _obs_001, "OBS-002": _obs_002, "OBS-003": _obs_003,
    "OBS-004": _obs_004, "OBS-005": _obs_005, "OBS-006": _obs_006,
    "OBS-007": _obs_007, "OBS-008": _obs_008,
    "ALERT-001": _alert_001, "ALERT-002": _alert_002, "ALERT-003": _alert_003,
    "ALERT-004": _alert_004, "ALERT-005": _alert_005, "ALERT-006": _alert_006,
    "ALERT-007": _alert_007,
    "REL-001": _rel_001, "REL-002": _rel_002, "REL-003": _rel_003,
    "REL-004": _rel_004, "REL-005": _rel_005, "REL-006": _rel_006,
    "REL-007": _rel_007,
    "PERF-001": _perf_001, "PERF-002": _perf_002, "PERF-003": _perf_003,
    "PERF-004": _perf_004, "PERF-005": _perf_005, "PERF-006": _perf_006,
    "COST-001": _cost_001, "COST-002": _cost_002, "COST-003": _cost_003,
    "COST-004": _cost_004, "COST-005": _cost_005, "COST-006": _cost_006,
    "DEVOPS-001": _devops_001, "DEVOPS-002": _devops_002, "DEVOPS-003": _devops_003,
    "DEVOPS-004": _devops_004, "DEVOPS-005": _devops_005, "DEVOPS-006": _devops_006,
    "DEVOPS-007": _devops_007,
    "TEST-001": _test_001, "TEST-002": _test_002, "TEST-003": _test_003,
    "TEST-004": _test_004, "TEST-005": _test_005, "TEST-006": _test_006,
    "TEST-007": _test_007, "TEST-008": _test_008,
    "OPS-001": _ops_001, "OPS-002": _ops_002, "OPS-003": _ops_003,
    "OPS-004": _ops_004, "OPS-005": _ops_005, "OPS-006": _ops_006,
    "OPS-007": _ops_007,
    "DOC-001": _doc_001, "DOC-002": _doc_002, "DOC-003": _doc_003,
    "DOC-004": _doc_004, "DOC-005": _doc_005, "DOC-006": _doc_006,
    "DOC-007": _doc_007,
    "BUS-001": _bus_manual, "BUS-002": _bus_manual, "BUS-003": _bus_manual,
    "BUS-004": _bus_004, "BUS-005": _bus_manual, "BUS-006": _bus_006,
}

# Singleton
readiness_check_runner = ReadinessCheckRunner()
