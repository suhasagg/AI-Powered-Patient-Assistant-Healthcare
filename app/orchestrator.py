import uuid
from app.models import AssistRequest, AssistResponse, Intent
from app.agents import symptom, appointment, faq, insurance
from app.audit.service import emit

async def assist(req: AssistRequest) -> AssistResponse:
    correlation_id = str(uuid.uuid4())
    runners = {
        Intent.symptom: symptom.run,
        Intent.appointment: appointment.run,
        Intent.faq: faq.run,
        Intent.insurance: insurance.run,
    }
    result = await runners[req.intent](req.message, correlation_id)
    emit("assistant_completed", correlation_id, req.tenant_id, result.agent, result.status)
    return result
