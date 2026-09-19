from app.models import AssistResponse, Source
from app.rag.store import retrieve
from app.llm.gateway import generate

async def run(message: str, correlation_id: str) -> AssistResponse:
    docs = retrieve(message, "faq")
    if not docs:
        return AssistResponse(
            correlation_id=correlation_id, agent="medical_faq", status="unsupported",
            message="I do not have approved knowledge supporting an answer to that question. Please ask a qualified healthcare professional.",
            disclaimer="Educational information only."
        )
    evidence = "\n".join(d.text for d in docs)
    answer = await generate("Answer the medical FAQ using only approved evidence", message, evidence)
    return AssistResponse(
        correlation_id=correlation_id, agent="medical_faq", status="ok",
        message=answer,
        sources=[Source(source_id=d.source_id, title=d.title, version=d.version) for d in docs],
        disclaimer="Educational information only; not individualized medical advice."
    )
