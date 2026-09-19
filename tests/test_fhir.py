import pytest
from app.integrations.fhir import request_appointment

@pytest.mark.asyncio
async def test_idempotent_booking():
    a = await request_appointment("slot-101", "u1", "checkup", "key-1")
    b = await request_appointment("slot-101", "u1", "checkup", "key-1")
    assert a == b
