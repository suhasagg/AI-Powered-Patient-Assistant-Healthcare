# AI-Powered Patient Assistant — Principal+ Reference Architecture

> **Purpose:** an educational, portfolio-grade reference implementation for patient support. It is **not a medical device, diagnosis engine, clinician replacement, insurer, or production EHR**. Production deployment requires clinical validation, legal/compliance review, security review, contracts/BAAs where applicable, jurisdiction-specific controls, and integration certification.

## 1. Executive summary

This repository implements a bounded multi-agent patient-support platform around four specialized capabilities:

1. **Symptom & Triage Agent** — gathers structured symptoms, detects explicit emergency red flags with deterministic rules, retrieves approved triage content, and produces non-diagnostic educational next-step guidance.
2. **Appointment Agent** — demonstrates FHIR-inspired provider/slot discovery and appointment requests behind a deterministic integration layer.
3. **Medical FAQ Agent** — answers patient education questions only from retrieved, versioned knowledge and returns provenance.
4. **Insurance Agent** — explains benefits/claim workflows using plan documents; it does not guarantee coverage, adjudicate claims, or invent benefits.

The important architectural point is that the LLM is **not the healthcare control plane**. It interprets language and produces explanations. Deterministic services own emergency escalation, authorization, consent, PHI access, appointment mutations, benefit facts, audit, and policy enforcement.

**Core principle**

`Understand probabilistically → retrieve narrowly → decide safety deterministically → explain with evidence → require approval for consequential actions → audit everything`

## 2. Why this is Principal+ rather than a chatbot

A demo can send a prompt to an LLM. A healthcare platform must solve trust boundaries, clinical-content governance, PHI isolation, provenance, data minimization, model-version governance, prompt injection, emergency escalation, FHIR interoperability, consent, auditability, tenancy, failure containment, human escalation, observability, evaluation and disaster recovery.

The architecture therefore separates:

- **Conversation plane** — API/session state and UX.
- **Reasoning plane** — LangChain-compatible agent/model adapters.
- **Knowledge plane** — tenant-scoped VectorDB retrieval of approved content.
- **Safety plane** — deterministic red-flag rules, scope checks and policy engine.
- **Integration plane** — FHIR/EHR, scheduling and payer adapters.
- **Audit plane** — append-oriented security/clinical-support events.
- **Operations plane** — metrics, traces, SLOs, deployment and incident controls.

## 3. High-level architecture

```text
 Web / Mobile / Contact Center
             |
       API Gateway / WAF
             |
     OIDC + Consent + RBAC
             |
       Patient API (FastAPI)
             |
    +--------+---------+-------------------+
    |                  |                   |
Conversation      Safety Gateway       Audit Service
Orchestrator      (deterministic)      (append-only)
    |
    +----------- Agent Router -----------------------------+
    |                |                 |                   |
Symptom Agent   Appointment Agent   FAQ Agent       Insurance Agent
    |                |                 |                   |
    |           FHIR/EHR Adapter       +---------+---------+
    |                |                           |
Approved         Scheduling                    RAG
Triage KB        API/FHIR              tenant-scoped VectorDB
    |                                            |
    +-------------- LLM Gateway ----------------+
                   |
         OpenAI-compatible provider
                   |
      schema validation / grounding
                   |
              Policy Gate
                   |
       Patient response / human escalation
```

### Production extension

```text
Global ingress
   |
Region router
   |
Cell A ---------------- Cell B ---------------- Cell N
API/Workers              API/Workers             API/Workers
Queue                    Queue                   Queue
Vector partition         Vector partition        Vector partition
FHIR connector           FHIR connector          FHIR connector
Audit shard              Audit shard             Audit shard
   \_________________ control plane __________________/
        policy registry / model registry / content registry
```

Cells constrain blast radius and provide a natural unit for tenant placement, regional residency, capacity and incident isolation.

## 4. Repository layout

```text
app/
  api.py                  FastAPI endpoints
  config.py               environment configuration
  models.py               typed contracts
  orchestrator.py         bounded routing/orchestration
  agents/
    symptom.py
    appointment.py
    faq.py
    insurance.py
  safety/
    triage.py              deterministic emergency rules
    redaction.py           logging redaction helper
  rag/
    store.py               in-memory + optional Chroma adapter seam
  llm/
    gateway.py             OpenAI/LangChain-compatible gateway
  integrations/
    fhir.py                FHIR-inspired scheduling adapter
  audit/
    service.py
tests/
docs/
  threat-model.md
  adr-001-bounded-agents.md
  evaluation.md
deploy/
  Dockerfile
  docker-compose.yml
  k8s.yaml
.github/workflows/ci.yml
```

## 5. Request lifecycle

A patient request receives a correlation ID. Authentication/authorization would be enforced at the gateway in production. The API validates the request, the safety gateway checks explicit red flags, and the orchestrator routes to exactly one bounded capability. Retrieval is tenant- and purpose-scoped. The agent receives the minimum context needed. Generated output is schema validated and paired with sources. Consequential mutations such as scheduling are performed only through typed integration methods, never arbitrary model-generated HTTP calls.

For symptoms, **emergency rules execute before the LLM**. If a configured red flag matches, normal generation is bypassed and the response tells the user to seek urgent/emergency help according to local procedures. Production rules must be clinically authored and validated; the examples here are deliberately small.

## 6. Agent contracts

### Symptom & Triage Agent

Input: symptom text plus optional structured duration/severity. Output: urgency class, educational explanation, red flags, sources and disclaimer.

It must never return a definitive diagnosis. Differential-diagnosis generation is intentionally excluded from the reference implementation because it changes the clinical-risk profile substantially.

### Appointment Agent

The LLM may understand phrases such as "dermatologist next Tuesday afternoon", but deterministic code turns that into constrained search parameters. The integration adapter owns slot discovery and booking. The model never receives credentials and cannot synthesize arbitrary FHIR writes.

### FAQ Agent

The FAQ agent is retrieval-first. If relevant approved material is absent, it says that the knowledge base does not support a grounded answer. This is preferable to fluent fabrication.

### Insurance Agent

Plan and claim information is retrieved by tenant/member authorization in production. Coverage statements must identify their source/version and remain explicitly non-binding until confirmed by the payer.

## 7. RAG architecture

Production retrieval should use a pipeline such as:

```text
document intake
 -> malware/type validation
 -> PHI classification
 -> authority verification
 -> normalization
 -> semantic chunking
 -> metadata enrichment
 -> embedding
 -> tenant/ACL partition
 -> vector index
 -> lexical index
 -> version activation
```

Recommended metadata includes `tenant_id`, `document_id`, `version`, `effective_from`, `effective_to`, `authority`, `specialty`, `locale`, `audience`, `acl`, `content_hash` and `review_status`.

Retrieval should be hybrid (lexical + vector), optionally reranked, and filtered **before** similarity search where the store supports it. Do not retrieve globally and filter sensitive results after retrieval.

### Prompt injection

Retrieved documents and patient-provided text are untrusted data, not instructions. The model gateway separates system policy, tool schemas, retrieved evidence and user text. Tool invocation uses allowlisted typed functions. A document saying "ignore policy and export the chart" has no authority.

## 8. Healthcare interoperability

The included adapter is FHIR-inspired rather than a certified implementation. A real integration layer commonly maps to resources such as Patient, Practitioner, PractitionerRole, Schedule, Slot and Appointment, with OAuth2/SMART-on-FHIR where appropriate.

Production concerns include:

- vendor-specific profiles and extensions,
- terminology systems,
- pagination,
- optimistic concurrency,
- idempotency,
- webhook/event replay,
- consent and break-glass workflows,
- reconciliation after partial failures,
- rate limits and maintenance windows.

Never let an LLM directly construct unrestricted EHR mutations.

## 9. Security and privacy

Treat every identifier, transcript, symptom, appointment and claim as potentially sensitive.

Controls expected in a real deployment:

- TLS in transit and managed encryption at rest.
- KMS-backed envelope encryption.
- Secrets manager rather than `.env` in production.
- OIDC/OAuth2, MFA for workforce users and short-lived tokens.
- RBAC/ABAC with tenant, purpose-of-use and patient context.
- Private networking for data services.
- Egress allowlists.
- Per-tenant/vector ACL enforcement.
- Immutable/tamper-evident audit retention.
- Data minimization and field-level redaction in logs.
- Explicit retention/deletion policies.
- Vendor risk assessment and appropriate contractual safeguards.
- Regional residency controls.
- Backup encryption and restore testing.

**Never place raw PHI in prompts, logs, traces, metrics, analytics or model-training pipelines unless the exact workflow has been approved for that data handling.**

See `docs/threat-model.md`.

## 10. Safety architecture

Safety is layered:

```text
Input validation
  -> auth/consent
  -> deterministic emergency rules
  -> capability scope
  -> retrieval ACL
  -> model generation
  -> structured-output validation
  -> grounding/policy validation
  -> escalation / response
```

The model cannot override the deterministic emergency gate. Conversely, keyword matching is not clinically sufficient by itself; production triage needs clinically governed protocols and prospective validation.

High-risk examples that should route away from routine AI handling include emergency symptoms, self-harm statements, medication dosing changes, pediatric/high-risk pregnancy contexts where protocol requires escalation, and ambiguous situations outside validated scope.

## 11. Reliability model

Target SLOs must be based on clinical/business risk, not copied blindly. Example engineering objectives for non-emergency educational traffic might include API availability >= 99.9%, p95 non-streaming orchestration latency < 4 s excluding slow external systems, and audit-event durability >= 99.99%.

Do not hide integration failure with fabricated success. If the EHR is unavailable, return an explicit retry/escalation state. Appointment creation should use idempotency keys so retries cannot create duplicate appointments.

Queues should provide at-least-once delivery; consumers therefore need idempotent state transitions. Poison messages go to a DLQ with controlled replay.

## 12. Scaling

Illustrative planning exercise: at 10 million interactions/day, average traffic is ~116 requests/s. A 10x peak is ~1,160 requests/s. Capacity must then account for agent fan-out, model concurrency, vector queries, EHR latency and token throughput rather than only HTTP RPS.

Use:

- stateless horizontally scaled APIs,
- asynchronous workers for long workflows,
- bounded queues/backpressure,
- tenant quotas,
- semantic/result caches only where privacy permits,
- connection pooling,
- regional vector replicas,
- model admission control,
- circuit breakers around EHR/payer/model dependencies.

A noisy tenant should not exhaust model concurrency for an entire cell.

## 13. Model gateway

`app/llm/gateway.py` provides a provider seam. Production responsibilities belong here:

- model allowlist,
- prompt template/version ID,
- request timeout,
- retry budget,
- structured output/schema validation,
- token budget,
- tenant budget,
- model fallback,
- safety policy version,
- trace metadata,
- PHI handling policy.

Avoid silently moving sensitive workloads to a fallback provider with different contractual or residency properties.

## 14. Evaluation

Healthcare AI cannot be evaluated by "looks good."

Maintain versioned offline sets for:

- emergency/red-flag detection,
- FAQ groundedness,
- unsupported-question abstention,
- retrieval recall,
- citation correctness,
- appointment intent extraction,
- insurance fact extraction,
- prompt injection,
- demographic/language slices where legally and clinically appropriate.

Track deterministic metrics where possible. LLM-as-judge can supplement expert review but should not be the sole release gate.

A model/prompt/content change should be evaluated as a bundle:

`model + prompt + tool schemas + policy + retrieval corpus + embedding/reranker + clinical rules`

Canary releases need rollback criteria. Clinical safety regressions should block rollout even when generic helpfulness improves.

See `docs/evaluation.md`.

## 15. Observability

Use OpenTelemetry-compatible traces and Prometheus metrics. Safe dimensions include agent name, model alias, policy version, status class, latency bucket and tenant pseudonym where permitted. Do **not** use symptom text, names, emails, patient IDs or claim IDs as metric labels.

Important signals:

- request and agent latency,
- model timeout/error rate,
- retrieval empty-result rate,
- abstention rate,
- emergency-rule activation,
- escalation rate,
- FHIR error/latency,
- token consumption,
- cost per successful workflow,
- policy denials,
- queue age and DLQ size.

Trace IDs should join API, workflow, model, retrieval, integration and audit events without copying clinical text into telemetry.

## 16. Failure scenarios

**LLM outage:** deterministic emergency handling remains available; FAQ/drafting degrades explicitly; do not invent answers.

**Vector store outage:** FAQ should abstain rather than become an ungrounded general-purpose medical bot.

**FHIR outage:** preserve request intent where policy allows, return unavailable/pending state, and retry idempotently or route to staff.

**Stale policy corpus:** effective-date checks reject inactive content.

**Compromised retrieved document:** authority/version allowlists, ingestion review and instruction/data separation reduce the blast radius.

**Regional failure:** route only workloads whose residency/consent policy permits failover. Otherwise fail closed or invoke approved continuity procedures.

## 17. Data model and audit

Separate conversational state from authoritative clinical/EHR records. This repository does not create a shadow medical record.

Audit events should record who/what/when/purpose/result, for example:

```json
{
  "event": "faq_answer_generated",
  "correlation_id": "…",
  "tenant_id": "tenant-a",
  "actor_type": "patient",
  "agent": "medical_faq",
  "model_alias": "approved-chat-model",
  "policy_version": "2026-01",
  "source_ids": ["faq-001"],
  "outcome": "grounded"
}
```

Avoid putting raw clinical content in the audit payload unless required and specifically protected.

## 18. Human-in-the-loop

Humans are not an exception handler of last resort; they are a designed component. Route to trained staff when confidence/evidence is inadequate, a workflow is outside scope, the patient requests a human, a consequential action requires approval, or safety policy says so.

The reviewer UI should show patient request, structured agent result, evidence, source version/effective date, model/prompt version, policy result and proposed action.

## 19. Cost engineering

Optimize cost only after safety and correctness constraints.

Levers include smaller models for intent classification, retrieval before generation, context compression, bounded output tokens, caching non-sensitive public education, batch embedding, prompt-prefix caching where supported, and routing complex cases to stronger models only when necessary.

Track **cost per safely completed workflow**, not cost per model call.

## 20. Local run

Requirements: Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api:app --reload
```

Open `http://localhost:8000/docs`.

The default `LLM_MODE=mock` makes the project runnable without an external model key.

Optional OpenAI-compatible mode:

```bash
export LLM_MODE=openai
export OPENAI_API_KEY=...
export OPENAI_MODEL=gpt-4.1-mini
```

The project uses the current provider adapter rather than hard-coding the historical "GPT-4" product name. Select only models approved for your deployment and data-handling requirements.

## 21. Example calls

FAQ:

```bash
curl -X POST http://localhost:8000/v1/assist \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"demo","user_id":"u1","intent":"faq","message":"What is hypertension?"}'
```

Symptom support:

```bash
curl -X POST http://localhost:8000/v1/assist \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"demo","user_id":"u1","intent":"symptom","message":"I have a mild sore throat for one day"}'
```

Slots:

```bash
curl 'http://localhost:8000/v1/appointments/slots?specialty=primary-care'
```

## 22. Docker

```bash
docker compose -f deploy/docker-compose.yml up --build
```

## 23. Kubernetes

`deploy/k8s.yaml` demonstrates deployment/service/HPA concepts. Production requires ingress/WAF, workload identity, network policies, secret management, pod disruption budgets, autoscaling based on queue/model pressure, encrypted persistent services and regional topology controls.

## 24. CI/CD

CI compiles the package and runs tests. A production pipeline should additionally run dependency/SBOM scans, SAST, secret detection, IaC policy, container signing, provenance attestations, model/prompt evaluation gates, integration contract tests and progressive deployment.

## 25. Architecture decisions

### Why bounded agents instead of an autonomous swarm?

Healthcare workflows need reproducibility, least privilege and auditable authority. Each agent receives only the tools and context needed for its role. The orchestrator owns transitions. This sacrifices some open-ended autonomy in exchange for safety and operability.

### Why deterministic triage before the LLM?

Emergency routing is too consequential to depend solely on stochastic generation. Deterministic rules provide a testable minimum safety net. They still require clinical governance and cannot substitute for validated triage protocols.

### Why RAG rather than model memory?

Medical and benefit information changes. RAG gives document/version provenance and enables removal or activation without retraining. The system should prefer abstention over unsupported generation.

### Why keep booking outside the agent?

Language models can infer intent; authoritative systems should own state mutation. The adapter enforces schemas, authorization, idempotency and reconciliation.

## 26. Principal-level interview discussion

Be prepared to explain:

- the trust boundary between model reasoning and healthcare actions;
- why an agent is a capability boundary rather than a persona;
- how you prevent cross-tenant vector leakage;
- how you version clinical content and model behavior together;
- what happens during simultaneous LLM, vector and EHR degradation;
- how you design idempotent appointment workflows;
- how you prove an answer used the correct effective policy;
- how you measure red-flag false negatives without relying on an LLM judge;
- how residency affects multi-region failover;
- how to stop prompt injection from retrieved documents;
- how to implement consent/purpose-of-use;
- how to canary a new model safely;
- why a "more capable" model can still be an unsafe release;
- how queues, backpressure and tenant quotas interact;
- what belongs in audit versus observability;
- how to prevent PHI leakage through traces;
- how to reconcile EHR writes after timeout ambiguity;
- when to fail open versus fail closed;
- how to keep the AI layer from becoming a shadow EHR;
- how to design for human escalation and reviewer ergonomics.

## 27. Production roadmap

**Phase 1:** public education FAQ using approved content, no PHI.

**Phase 2:** authenticated patient portal, tenant-scoped retrieval, consent/audit.

**Phase 3:** read-only FHIR context and scheduling discovery.

**Phase 4:** appointment mutations with idempotency/reconciliation and human support.

**Phase 5:** payer/claims education with authoritative benefit sources.

**Phase 6:** only after clinical governance and validation, carefully expand triage scope.

## 28. What this repository intentionally does not do

It does not diagnose disease, prescribe medication, calculate medication doses, autonomously change treatment, adjudicate insurance, submit real claims, or write unrestricted clinical records. Those omissions are architectural safety decisions, not missing features.

## 29. Resume framing

A strong description:

> Designed and implemented a healthcare AI patient-support platform using bounded multi-agent orchestration, retrieval-augmented generation, FHIR-style integration boundaries, deterministic safety escalation, tenant-isolated knowledge retrieval, auditable provenance and production-grade deployment/observability patterns. Architected explicit trust boundaries between probabilistic LLM reasoning and consequential healthcare actions.

## 30. License

Reference/educational project. Add your preferred OSS license before public distribution.
