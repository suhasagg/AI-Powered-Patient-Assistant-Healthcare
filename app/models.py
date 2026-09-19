from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

class Intent(str, Enum):
    symptom = "symptom"
    appointment = "appointment"
    faq = "faq"
    insurance = "insurance"

class AssistRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=100)
    user_id: str = Field(min_length=1, max_length=100)
    intent: Intent
    message: str = Field(min_length=1, max_length=8000)

class Source(BaseModel):
    source_id: str
    title: str
    version: str

class AssistResponse(BaseModel):
    correlation_id: str
    agent: str
    status: Literal["ok", "escalate", "unsupported", "unavailable"]
    message: str
    sources: list[Source] = []
    disclaimer: str | None = None

class Slot(BaseModel):
    slot_id: str
    specialty: str
    start: str
    practitioner: str

class AppointmentRequest(BaseModel):
    tenant_id: str
    user_id: str
    slot_id: str
    reason: str = Field(max_length=1000)
    idempotency_key: str
