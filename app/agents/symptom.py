from app.models import AssistResponse, Source
from app.safety.triage import evaluate
from app.rag.store import retrieve
from app.llm.gateway import generate

async def run(message: str, correlation_id: str) -> AssistResponse:
    decision = evaluate(message)
    if decision.emergency:
        return AssistResponse(
            correlation_id=correlation_id,
            agent="symptom_checker",
            status="escalate",
            message=f"Your message includes a possible emergency warning sign ({decision.reason}). Seek urgent/emergency medical help now using your local emergency service or nearest emergency department. Do not rely on this assistant for emergency assessment.",
            disclaimer="This assistant does not diagnose medical conditions."
        )
    docs = retrieve(message, "symptom")
    evidence = "\n".join(d.text for d in docs)
    answer = await generate(
        "Provide non-diagnostic symptom education and explain that worsening, severe, persistent, or concerning symptoms need professional assessment",
        message, evidence
    )
    return AssistResponse(
        correlation_id=correlation_id, agent="symptom_checker", status="ok",
        message=answer,
        sources=[Source(source_id=d.source_id, title=d.title, version=d.version) for d in docs],
        disclaimer="Educational support only; this is not a diagnosis or treatment plan."
    )
