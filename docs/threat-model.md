# Threat model

## Assets
Patient identity/context, clinical-support text, appointments, benefit/claim information, credentials, vector documents, model prompts, audit records and integration tokens.

## Threats and controls

**Cross-tenant retrieval** — enforce tenant/ACL filters at retrieval time, separate encryption domains where required, authorization tests and canaries.

**Prompt injection** — retrieved/user text is untrusted; typed allowlisted tools; system policy cannot be overridden by content; no secrets in model context.

**PHI leakage to telemetry** — structured logging allowlist, redaction, no raw text in metric labels, restricted trace attributes.

**Over-privileged model** — credentials remain in deterministic adapters; model receives capabilities, not bearer tokens.

**Appointment replay** — idempotency keys, authoritative reconciliation and optimistic concurrency.

**Malicious document ingestion** — content-type validation, malware scan, authority verification, quarantine/review, version activation.

**Model/provider data exposure** — approved provider/model registry, contractual/data-processing controls, regional endpoints, explicit fallback policy.

**Insider access** — least privilege, MFA, just-in-time access, purpose-of-use, immutable audit and periodic access review.

**Availability attack** — WAF/rate limits, tenant quotas, queues/backpressure, circuit breakers and cell isolation.

## Abuse cases
A patient asks the model to ignore safety policy; a retrieved PDF contains tool instructions; a tenant attempts another tenant's source ID; a retry duplicates an appointment; a model fabricates insurance coverage; a user presents emergency language during an LLM outage. All should have deterministic tests.
