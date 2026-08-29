import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_failure_recovery_rag_service_unavailable():
    """
    Sprint 4 Failure Test:
    When RAG service fails / raises exception, backend must return controlled HTTP 503 response
    and NEVER fabricate false evidence.
    """
    with patch("src.services.ai_contracts.rag_service.MockRAGRetrieverService.retrieve_evidence", new_callable=AsyncMock) as mock_rag:
        mock_rag.side_effect = Exception("ChromaDB vector connection timed out")

        response = client.post(
            "/api/v1/evidence/search",
            json={"query": "rare neurological disorder treatment"}
        )

        assert response.status_code == 503
        data = response.json()
        assert "error" in data
        assert "message" in data["error"] or "detail" in data


def test_failure_recovery_invalid_document_upload():
    """
    Sprint 4 Failure Test:
    Uploading unsupported file formats (e.g. .exe, .sh) must return controlled HTTP 400 error.
    """
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("exploit.sh", b"#!/bin/bash echo hack", "application/x-sh")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_failure_recovery_nonexistent_referral():
    """
    Sprint 4 Failure Test:
    Querying non-existent referral ID must return HTTP 404 with standard error structure.
    """
    response = client.get("/api/v1/referrals/ref_nonexistent_999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
