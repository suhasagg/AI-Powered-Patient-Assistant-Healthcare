from app.rag.store import retrieve

def test_hypertension_retrieval():
    docs = retrieve("What is hypertension?", "faq")
    assert docs
    assert docs[0].source_id == "faq-001"
