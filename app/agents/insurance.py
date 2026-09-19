from app.models import AssistResponse, Source
from app.rag.store import retrieve
from app.llm.gateway import generate

async def run(message: str, correlation_id: str) -> AssistResponse:
    docs = retrieve(message, "insurance")
    if not docs:
        return AssistResponse(
            correlation_id=correlation_id, agent="insurance_advisor", status="unsupported",
            message="I do not have authoritative plan information for that request. Confirm coverage or claim status directly with the payer or benefits team.",
            disclaimer="Coverage is determined by the applicable plan and payer."
        )
    evidence = "\n".join(d.text for d in docs)
    answer = await generate("Explain the insurance or claims process without guaranteeing coverage", message, evidence)
    return AssistResponse(
        correlation_id=correlation_id, agent="insurance_advisor", status="ok",
        message=answer,
        sources=[Source(source_id=d.source_id, title=d.title, version=d.version) for d in docs],
        disclaimer="This explanation is non-binding; verify benefits with the payer."
    )
