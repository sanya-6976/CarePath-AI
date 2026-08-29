"""Tests for Medical Knowledge RAG API and engine."""

def test_rag_query_endpoint(client):
    payload = {
        "query": "What is the recommended treatment for community-acquired pneumonia?",
        "top_k": 2
    }
    response = client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert len(data["retrieved_chunks"]) > 0
    assert "synthesized_guideline_answer" in data
    assert len(data["citations"]) > 0
