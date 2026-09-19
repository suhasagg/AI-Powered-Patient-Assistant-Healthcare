from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    source_id: str
    title: str
    version: str
    text: str
    tags: tuple[str, ...]

DOCS = [
    Document("faq-001", "Hypertension education", "2026-01",
             "Hypertension means blood pressure that remains higher than the recommended range over time. Diagnosis requires appropriate measurements and clinical assessment. Lifestyle and treatment decisions should be discussed with a qualified clinician.",
             ("faq", "hypertension", "blood pressure")),
    Document("faq-002", "Common cold education", "2026-01",
             "Many uncomplicated colds improve with time and supportive care. Seek medical advice when symptoms are severe, persistent, worsening, or accompanied by concerning features.",
             ("faq", "cold", "sore throat")),
    Document("ins-001", "Demo claim workflow", "2026-01",
             "A typical claim workflow can include eligibility verification, claim submission, payer processing, explanation of benefits, and an appeal process. Actual coverage and timelines depend on the member's plan and payer.",
             ("insurance", "claim", "coverage", "appeal")),
    Document("triage-001", "Symptom support scope", "2026-01",
             "Online symptom support can provide general education and help identify when professional assessment may be appropriate, but it cannot establish a diagnosis.",
             ("symptom", "triage")),
]

def retrieve(query: str, intent: str, limit: int = 3) -> list[Document]:
    words = set(query.lower().replace("?", "").split())
    scored = []
    for d in DOCS:
        if intent not in d.tags and intent != "faq":
            continue
        hay = (d.text + " " + " ".join(d.tags)).lower()
        score = sum(1 for w in words if len(w) > 2 and w in hay)
        if score:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:limit]]
