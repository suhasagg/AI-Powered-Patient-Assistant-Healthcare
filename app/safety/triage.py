from dataclasses import dataclass

@dataclass(frozen=True)
class TriageDecision:
    emergency: bool
    reason: str | None = None

# Demonstration-only minimum safety net. Production rules require clinical governance.
RED_FLAGS = {
    "severe chest pain": "severe chest pain",
    "can't breathe": "severe breathing difficulty",
    "cannot breathe": "severe breathing difficulty",
    "unconscious": "loss of consciousness",
    "heavy bleeding": "heavy bleeding",
    "suicidal": "self-harm risk",
    "kill myself": "self-harm risk",
}

def evaluate(text: str) -> TriageDecision:
    lower = text.lower()
    for phrase, reason in RED_FLAGS.items():
        if phrase in lower:
            return TriageDecision(True, reason)
    return TriageDecision(False)
