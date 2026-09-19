# ADR-001 — Bounded agents over autonomous agents

## Decision
Use a deterministic orchestrator with capability-specific agents and typed tool adapters.

## Context
Healthcare actions have asymmetric risk. Free-form autonomous planning makes authorization, reproducibility, testing and incident analysis difficult.

## Consequences
Each agent has a smaller permission surface. The model can recommend a typed operation but cannot acquire new tools or credentials. This limits flexibility but materially improves auditability, least privilege, testing and failure containment.
