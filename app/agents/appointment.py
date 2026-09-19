from app.models import AssistResponse

async def run(message: str, correlation_id: str) -> AssistResponse:
    return AssistResponse(
        correlation_id=correlation_id,
        agent="appointment_scheduler",
        status="ok",
        message="Use the typed slot-discovery endpoint to view available specialties/slots, then submit an appointment request with an idempotency key. In production, natural-language intent is converted into constrained parameters before the FHIR adapter is called.",
        disclaimer="The demo does not connect to a real EHR."
    )
