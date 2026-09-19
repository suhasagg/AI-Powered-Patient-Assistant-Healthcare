import logging
from app.safety.redaction import redact_for_logs

logger = logging.getLogger("audit")

def emit(event: str, correlation_id: str, tenant_id: str, agent: str, outcome: str) -> None:
    # Production: write to durable/tamper-evident audit storage.
    logger.info({
        "event": event,
        "correlation_id": correlation_id,
        "tenant_id": redact_for_logs(tenant_id),
        "agent": agent,
        "outcome": outcome,
    })
