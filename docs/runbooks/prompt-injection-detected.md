# Prompt Injection Detected

## Alert meaning
Input, retrieved content, or generated content contained prompt injection signals.

## Severity
SEV0_CRITICAL for confirmed exploit path, otherwise SEV1_HIGH.

## Possible causes
Malicious document content, adversarial case notes, unsafe prompt composition, or missing content filters.

## Immediate triage steps
Isolate the triggering case, preserve evidence, and verify whether the model output exposed secrets or bypassed instructions.

## KQL queries to run
Run `monitoring/kql/prompt-injection-detected.kql`.

## Application logs to check
Inspect `PROMPT_INJECTION_DETECTED`, `SECURITY_EVENT_RECORDED`, and related LLM call traces.

## Azure resources to inspect
Azure OpenAI content filters, policy document source, backend logs, and Key Vault access logs.

## Safe mitigation steps
Disable affected document source, force human-only review, rotate exposed secrets if any, and tighten guardrails.

## Escalation path
Security incident response, AI governance, and platform owner.

## When to resolve
Resolve after exploit path is blocked and no sensitive data exposure remains.

## Post-incident review notes
Record attack text, impact assessment, and guardrail changes.
