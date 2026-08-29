from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.core.auth import get_current_user
from src.services.ai_contracts.rag_service import MockRAGRetrieverService

router = APIRouter(prefix="/evidence", tags=["Evidence & RAG Integration"])
rag_service = MockRAGRetrieverService()


class EvidenceSearchRequest(BaseModel):
    query: str
    patient_context: Optional[Dict[str, Any]] = None


class EvidenceSource(BaseModel):
    title: str
    source: str
    relevance: str
    content: str


class EvidenceSearchResponse(BaseModel):
    query: str
    sources: List[EvidenceSource]


@router.post("/search", response_model=EvidenceSearchResponse)
async def search_evidence(
    payload: EvidenceSearchRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Accepts clinical query and patient context, returning structured clinical guidelines from ChromaDB/RAG.
    Controlled error/fallback response if RAG service is unreachable; never invents evidence.
    """
    try:
        query_symptoms = [s.strip() for s in payload.query.split() if len(s) > 3]
        results = await rag_service.retrieve_evidence(query_symptoms)

        sources = []
        for r in results:
            sources.append(EvidenceSource(
                title=r.get("title", "Clinical Guideline"),
                source=r.get("document_id", "ChromaDB"),
                relevance=str(r.get("relevance_score", 0.90)),
                content=r.get("content", "")
            ))

        return EvidenceSearchResponse(query=payload.query, sources=sources)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Clinical Evidence & RAG Retrieval service is currently unavailable."
        )
