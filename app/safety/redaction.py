import re

EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d .()-]{7,}\d)(?!\d)")

def redact_for_logs(text: str) -> str:
    text = EMAIL.sub("[EMAIL]", text)
    return PHONE.sub("[PHONE]", text)
