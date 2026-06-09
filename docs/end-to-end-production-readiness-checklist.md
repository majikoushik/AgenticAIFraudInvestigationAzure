# End-to-End Production Readiness Checklist

**System:** Agentic AI Banking Fraud Investigation System  
**Version:** MVP — Azure-Ready  
**Document Status:** Living document — updated with each assessment cycle  

---

## Overview

This document defines the complete production readiness framework for the Agentic AI Banking Fraud Investigation System. It covers 20 domains and 120+ automated and manual checks that must be evaluated before any deployment to production.

The framework is implemented as:
- **Backend module:** `backend/app/readiness/`
- **API endpoints:** `POST /api/v1/readiness/assessments/run` and related endpoints
- **Frontend pages:** `/readiness`, `/readiness/risks`, `/readiness/checklist`, `/readiness/[id]`
- **CLI script:** `scripts/readiness/run-readiness-assessment.py`
- **Monitoring:** `monitoring/kql/`, `monitoring/alerts/`, `docs/runbooks/`

---

## Go-Live Decision Criteria

| Decision | Conditions |
| --- | --- |
| **✅ READY** | Score ≥ 90, blockers = 0, high risks = 0 |
| **⚠️ READY WITH RISKS** | Score ≥ 70, blockers = 0, high risks ≤ 3 |
| **🔵 MANUAL REVIEW REQUIRED** | >30% manual review pending |
| **❌ NOT READY** | Any BLOCKER-severity check has FAILED |

---

## Readiness Domains

### A. Architecture
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| ARCH-001 | High-level architecture documented | MEDIUM | MANUAL |
| ARCH-002 | Component boundaries are defined | MEDIUM | HYBRID |
| ARCH-003 | Frontend, backend, agents, RAG, infra folders exist | HIGH | AUTOMATED |
| ARCH-004 | Azure service mapping documented | MEDIUM | MANUAL |
| ARCH-005 | Local and production modes are separated | HIGH | AUTOMATED |

### B. Security
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| SEC-001 | No secrets committed to repository | **BLOCKER** | AUTOMATED |
| SEC-002 | Secret redaction utility exists | HIGH | AUTOMATED |
| SEC-003 | Security health endpoint exists | HIGH | AUTOMATED |
| SEC-004 | Admin APIs do not expose secrets | **BLOCKER** | HYBRID |
| SEC-005 | Frontend does not expose backend secrets | **BLOCKER** | AUTOMATED |
| SEC-006 | Security runbooks exist | MEDIUM | AUTOMATED |

### C. Identity and Access
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| IAM-001 | Entra ID authentication structure exists | **BLOCKER** | AUTOMATED |
| IAM-002 | Local auth mode exists for development | HIGH | AUTOMATED |
| IAM-003 | Backend role-based permissions are enforced | **BLOCKER** | AUTOMATED |
| IAM-004 | Auditor role is read-only | HIGH | AUTOMATED |
| IAM-005 | Admin-only endpoints are protected | **BLOCKER** | AUTOMATED |
| IAM-006 | Auth route documentation exists | LOW | AUTOMATED |

### D. Secrets and Key Management
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| KEY-001 | Key Vault provider exists | HIGH | AUTOMATED |
| KEY-002 | Environment provider exists for local mode | HIGH | AUTOMATED |
| KEY-003 | Managed identity support exists | HIGH | AUTOMATED |
| KEY-004 | Key Vault Bicep module exists | MEDIUM | AUTOMATED |
| KEY-005 | Secret values not returned in health/admin APIs | **BLOCKER** | HYBRID |
| KEY-006 | No secrets in Bicep parameter files | **BLOCKER** | AUTOMATED |

### E. Networking
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| NET-001 | Private endpoint Bicep module exists | HIGH | AUTOMATED |
| NET-002 | Private DNS zone module exists | HIGH | AUTOMATED |
| NET-003 | Public network access flags exist | HIGH | AUTOMATED |
| NET-004 | Container Apps VNet integration documented | MEDIUM | MANUAL |
| NET-005 | Network hardening documentation exists | MEDIUM | AUTOMATED |

### F. AI Safety and Guardrails
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| AI-001 | Human review is always required | **BLOCKER** | AUTOMATED |
| AI-002 | Guardrail engine exists | HIGH | AUTOMATED |
| AI-003 | PII redaction before LLM calls exists | **BLOCKER** | AUTOMATED |
| AI-004 | Prompt injection detector exists | HIGH | AUTOMATED |
| AI-005 | Output validator exists | HIGH | AUTOMATED |
| AI-006 | Direct fraud accusation language is blocked | **BLOCKER** | HYBRID |
| AI-007 | LLM output JSON validation exists | HIGH | AUTOMATED |
| AI-008 | Fallback mode exists when LLM fails | HIGH | AUTOMATED |

### G. RAG and Knowledge Grounding
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| RAG-001 | Azure AI Search retriever exists | HIGH | AUTOMATED |
| RAG-002 | Local fallback retriever exists | HIGH | AUTOMATED |
| RAG-003 | Policy index schema exists | MEDIUM | AUTOMATED |
| RAG-004 | Historical case index schema exists | MEDIUM | AUTOMATED |
| RAG-005 | Citation builder exists | HIGH | AUTOMATED |
| RAG-006 | Citation validator exists | HIGH | AUTOMATED |
| RAG-007 | RAG evaluation dataset exists | MEDIUM | AUTOMATED |
| RAG-008 | RAG retrieval audit/telemetry exists | MEDIUM | AUTOMATED |

### H. Human in the Loop
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| HITL-001 | Human review workflow exists | **BLOCKER** | AUTOMATED |
| HITL-002 | Role-based review permissions exist | **BLOCKER** | AUTOMATED |
| HITL-003 | Evidence acknowledgement required | HIGH | HYBRID |
| HITL-004 | Policy acknowledgement required | HIGH | HYBRID |
| HITL-005 | Human override tracking exists | HIGH | AUTOMATED |
| HITL-006 | Case status lifecycle exists | HIGH | AUTOMATED |
| HITL-007 | Closed cases are terminal | HIGH | AUTOMATED |

### I. Audit and Compliance
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| AUD-001 | Structured audit service exists | **BLOCKER** | AUTOMATED |
| AUD-002 | Audit events stored locally for MVP | HIGH | AUTOMATED |
| AUD-003 | Audit metadata sanitizer exists | HIGH | AUTOMATED |
| AUD-004 | Human decisions are audited | **BLOCKER** | AUTOMATED |
| AUD-005 | AI investigation events are audited | HIGH | AUTOMATED |
| AUD-006 | Admin config changes are audited | HIGH | AUTOMATED |
| AUD-007 | Compliance export exists | HIGH | AUTOMATED |

### J. Data Retention
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| RET-001 | Data category enum exists | HIGH | AUTOMATED |
| RET-002 | Retention policy registry exists | HIGH | AUTOMATED |
| RET-003 | Legal hold service exists | HIGH | AUTOMATED |
| RET-004 | Purge defaults to dry-run | HIGH | AUTOMATED |
| RET-005 | Legal hold blocks purge | **BLOCKER** | AUTOMATED |
| RET-006 | Compliance export redaction exists | HIGH | AUTOMATED |
| RET-007 | Retention documentation exists | MEDIUM | AUTOMATED |

### K. Observability
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| OBS-001 | Correlation ID middleware exists | HIGH | AUTOMATED |
| OBS-002 | API telemetry middleware exists | HIGH | AUTOMATED |
| OBS-003 | Agent telemetry exists | HIGH | AUTOMATED |
| OBS-004 | RAG telemetry exists | HIGH | AUTOMATED |
| OBS-005 | LLM telemetry exists | HIGH | AUTOMATED |
| OBS-006 | Application Insights config supported | HIGH | AUTOMATED |
| OBS-007 | KQL queries exist | MEDIUM | AUTOMATED |
| OBS-008 | Observability dashboard exists | MEDIUM | AUTOMATED |

### L. Alerting and Incident Response
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| ALERT-001 | Alert severity enum exists | HIGH | AUTOMATED |
| ALERT-002 | Alert evaluator exists | HIGH | AUTOMATED |
| ALERT-003 | Incident lifecycle exists | HIGH | AUTOMATED |
| ALERT-004 | Runbooks exist | HIGH | AUTOMATED |
| ALERT-005 | Local alert simulation exists | MEDIUM | AUTOMATED |
| ALERT-006 | Alert/incident frontend dashboard exists | MEDIUM | AUTOMATED |
| ALERT-007 | Notification integration exists | MEDIUM | AUTOMATED |

### M. Reliability and Resilience
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| REL-001 | Retry logic exists for LLM calls | HIGH | AUTOMATED |
| REL-002 | Timeout handling exists | HIGH | AUTOMATED |
| REL-003 | Fallback mode exists | HIGH | AUTOMATED |
| REL-004 | Circuit breaker or placeholder exists | MEDIUM | MANUAL |
| REL-005 | Failed agent execution handled safely | HIGH | AUTOMATED |
| REL-006 | Investigation failure does not corrupt case state | HIGH | AUTOMATED |
| REL-007 | Dead-letter queue placeholder/documentation exists | LOW | MANUAL |

### N. Performance and Scalability
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| PERF-001 | Agent latency telemetry exists | MEDIUM | AUTOMATED |
| PERF-002 | RAG latency telemetry exists | MEDIUM | AUTOMATED |
| PERF-003 | LLM latency telemetry exists | MEDIUM | AUTOMATED |
| PERF-004 | Container scaling settings exist in Bicep | MEDIUM | AUTOMATED |
| PERF-005 | Load/performance test placeholders exist | LOW | MANUAL |
| PERF-006 | Top expensive/slow cases visible | LOW | AUTOMATED |

### O. Cost Management
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| COST-001 | Token usage capture exists | HIGH | AUTOMATED |
| COST-002 | Cost estimator exists | HIGH | AUTOMATED |
| COST-003 | Cost dashboard exists | MEDIUM | AUTOMATED |
| COST-004 | Budget status endpoint exists | MEDIUM | AUTOMATED |
| COST-005 | Cost anomaly detector exists | MEDIUM | AUTOMATED |
| COST-006 | Cost alert placeholder exists | MEDIUM | AUTOMATED |

### P. DevOps and Release Management
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| DEVOPS-001 | Azure DevOps pipeline exists | HIGH | AUTOMATED |
| DEVOPS-002 | Infra validation stage exists | HIGH | MANUAL |
| DEVOPS-003 | Security scan stage exists | HIGH | MANUAL |
| DEVOPS-004 | Bicep what-if script exists | MEDIUM | AUTOMATED |
| DEVOPS-005 | Environment parameter files exist | HIGH | AUTOMATED |
| DEVOPS-006 | Rollback guide exists | HIGH | AUTOMATED |
| DEVOPS-007 | No secrets in pipeline YAML | **BLOCKER** | AUTOMATED |

### Q. Testing and Quality
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| TEST-001 | Backend tests exist | HIGH | AUTOMATED |
| TEST-002 | Agent tests exist | HIGH | AUTOMATED |
| TEST-003 | RAG tests exist | HIGH | AUTOMATED |
| TEST-004 | Frontend TypeScript build passes | HIGH | AUTOMATED |
| TEST-005 | Security tests exist | HIGH | AUTOMATED |
| TEST-006 | AI evaluation tests exist | MEDIUM | AUTOMATED |
| TEST-007 | Human review workflow tests exist | HIGH | AUTOMATED |
| TEST-008 | Audit route tests exist | HIGH | AUTOMATED |

### R. Operations and Support
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| OPS-001 | Operations runbook exists | HIGH | AUTOMATED |
| OPS-002 | Incident response documentation exists | HIGH | AUTOMATED |
| OPS-003 | Monitoring guide exists | MEDIUM | AUTOMATED |
| OPS-004 | Rollback guide exists | HIGH | AUTOMATED |
| OPS-005 | Admin configuration panel exists | HIGH | AUTOMATED |
| OPS-006 | Notification system exists | MEDIUM | AUTOMATED |
| OPS-007 | Case assignment queue exists | HIGH | AUTOMATED |

### S. Documentation
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| DOC-001 | README exists | HIGH | AUTOMATED |
| DOC-002 | Architecture docs exist | HIGH | AUTOMATED |
| DOC-003 | Security docs exist | HIGH | AUTOMATED |
| DOC-004 | RAG docs exist | MEDIUM | AUTOMATED |
| DOC-005 | Deployment hardening docs exist | HIGH | AUTOMATED |
| DOC-006 | Data retention docs exist | HIGH | AUTOMATED |
| DOC-007 | Production readiness checklist docs exist | HIGH | AUTOMATED |

### T. Business Readiness
| Check ID | Title | Severity | Type |
| --- | --- | --- | --- |
| BUS-001 | Fraud investigator workflow documented | HIGH | MANUAL |
| BUS-002 | Human review policy documented | HIGH | MANUAL |
| BUS-003 | AI limitation statement documented | HIGH | MANUAL |
| BUS-004 | Business KPIs dashboard exists | MEDIUM | AUTOMATED |
| BUS-005 | Training/demo guide exists | MEDIUM | MANUAL |
| BUS-006 | Go-live risk register exists | HIGH | AUTOMATED |

---

## Production Sign-Off Requirements

Before go-live, the following sign-offs are required:

| Role | Responsibility |
| --- | --- |
| **Solution Architect** | Architecture and overall go-live decision |
| **Security Owner** | SEC, KEY, IAM, NET domain clearance |
| **AI Governance Team** | AI safety and guardrail clearance |
| **Compliance Officer** | AUD, RET, HITL, compliance clearance |
| **Fraud Operations Lead** | Business workflow and HITL readiness |
| **Platform / DevOps Owner** | OBS, ALERT, REL, DEVOPS clearance |
| **Business Sponsor** | Business readiness and KPI sign-off |

---

## How to Run an Assessment

### Via API (ADMIN role required)
```http
POST /api/v1/readiness/assessments/run
Authorization: X-Demo-Role: ADMIN
Content-Type: application/json

{
  "environment": "prod",
  "create_risks_from_failures": true,
  "comment": "Pre-release readiness check"
}
```

### Via CLI Script
```bash
python scripts/readiness/run-readiness-assessment.py --environment prod
```

### Via Frontend
Navigate to **Production Readiness** in the sidebar.

---

## Security Notes

- Assessment reports **never** contain raw secrets, API keys, tokens, or customer PII.
- Secret scanning returns **only** the file path and pattern type — never the matched value.
- Evidence submissions are stored as plain text descriptions.
- RUN_READINESS_ASSESSMENT permission is restricted to ADMIN role only.
- EXPORT_READINESS_REPORT permission is granted to ADMIN, COMPLIANCE_OFFICER, and AUDITOR.

---

## Related Documentation
- [Deployment Hardening Guide](./deployment-hardening-key-vault-private-endpoints-managed-identity.md)
- [Production Security Checklist](./production-security-checklist.md)
- [Data Retention Policy](./data-retention-compliance-policy.md)
- [Runbooks](./runbooks/)
- [Azure AI Search RAG Guide](./azure-ai-search-production-rag.md)
