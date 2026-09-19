from fastapi import FastAPI, Query
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from app.models import AssistRequest, AssistResponse, AppointmentRequest, Slot
from app.orchestrator import assist
from app.integrations.fhir import list_slots, request_appointment

app = FastAPI(
    title="AI Patient Assistant",
    version="1.0.0",
    description="Bounded multi-agent patient-support reference architecture."
)

REQUESTS = Counter("patient_assistant_requests_total", "Requests", ["route", "status"])
LATENCY = Histogram("patient_assistant_latency_seconds", "Request latency", ["route"])

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/v1/assist", response_model=AssistResponse)
async def assist_endpoint(req: AssistRequest):
    with LATENCY.labels("assist").time():
        result = await assist(req)
    REQUESTS.labels("assist", result.status).inc()
    return result

@app.get("/v1/appointments/slots", response_model=list[Slot])
async def slots(specialty: str = Query(default="primary-care")):
    return await list_slots(specialty)

@app.post("/v1/appointments/request")
async def appointment_request(req: AppointmentRequest):
    return await request_appointment(req.slot_id, req.user_id, req.reason, req.idempotency_key)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
