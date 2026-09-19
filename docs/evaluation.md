# Evaluation strategy

## Release unit
Evaluate model + prompt + retrieval corpus + embeddings/reranker + tool schemas + safety rules + policy version.

## Symptom safety
Create clinician-governed labeled scenarios. Measure red-flag sensitivity/recall and false-negative count as first-class release gates. Stratify by paraphrase, spelling noise and supported languages. The demo rules are not a validated triage protocol.

## RAG
Measure retrieval recall@k, source authority, effective-date correctness, groundedness, citation entailment and abstention on unsupported questions.

## Scheduling
Contract-test intent-to-parameter conversion, timezone/date normalization, slot race conditions, retries, timeout ambiguity and idempotency.

## Insurance
Test benefit/claim statements against authoritative plan fixtures. Penalize invented coverage, invented dollar values and guarantees.

## Security
Red-team prompt injection, cross-tenant source references, data exfiltration requests, malicious documents, Unicode obfuscation and tool-argument injection.

## Online monitoring
Monitor escalation, abstention, empty retrieval, integration failures, patient-reported issues and human overrides. Do not infer clinical safety solely from engagement metrics.

## Change management
Shadow -> offline gate -> limited canary -> human review -> progressive rollout. Roll back on predefined safety/reliability thresholds.
