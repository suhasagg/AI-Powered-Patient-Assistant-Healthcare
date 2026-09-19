from app.safety.triage import evaluate

def test_emergency_red_flag():
    assert evaluate("I have severe chest pain").emergency is True

def test_non_emergency_example():
    assert evaluate("mild sore throat today").emergency is False
