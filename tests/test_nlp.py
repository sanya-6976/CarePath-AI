"""Tests for Bio-NER Clinical NLP API and engine."""

def test_nlp_extract_endpoint(client):
    text = "Patient presents with cough, fever, and shortness of breath for 3 days. Denies chest pain. Diagnosed with pneumonia."
    response = client.post("/api/v1/nlp/extract", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "symptoms" in data
    assert "cough" in [s.lower() for s in data["symptoms"]]
    assert "pneumonia" in [d.lower() for d in data["diagnoses"]]
