"""Tests for API root and health check endpoints."""

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "CarePath AI" in data["message"]


def test_api_status(client):
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
