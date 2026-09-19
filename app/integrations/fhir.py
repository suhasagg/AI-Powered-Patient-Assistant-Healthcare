from app.models import Slot

# Demo adapter. Replace with SMART-on-FHIR / vendor APIs in production.
SLOTS = [
    Slot(slot_id="slot-101", specialty="primary-care", start="2026-09-21T10:00:00+05:30", practitioner="Demo Clinician A"),
    Slot(slot_id="slot-102", specialty="primary-care", start="2026-09-21T11:00:00+05:30", practitioner="Demo Clinician B"),
    Slot(slot_id="slot-201", specialty="dermatology", start="2026-09-22T15:00:00+05:30", practitioner="Demo Clinician C"),
]
_bookings: dict[str, dict] = {}

async def list_slots(specialty: str) -> list[Slot]:
    return [s for s in SLOTS if s.specialty == specialty]

async def request_appointment(slot_id: str, user_id: str, reason: str, idempotency_key: str) -> dict:
    if idempotency_key in _bookings:
        return _bookings[idempotency_key]
    if not any(s.slot_id == slot_id for s in SLOTS):
        return {"status": "unavailable", "message": "Slot was not found."}
    result = {
        "status": "requested",
        "appointment_id": f"demo-{len(_bookings)+1}",
        "slot_id": slot_id,
        "message": "Appointment request recorded by the demo adapter."
    }
    _bookings[idempotency_key] = result
    return result
