"""Medical Guidelines RAG API Endpoint."""
from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.rag_engine import rag_engine
from app.core.logging import logger

router = APIRouter(prefix="/rag", tags=["Medical Knowledge RAG"])


@router.post("/query", response_model=RAGQueryResponse, summary="Query clinical practice guidelines using semantic vector retrieval")
async def query_medical_rag(
    request: RAGQueryRequest
):
    """Retrieve evidence-based medical treatment guidelines matching patient symptoms or clinical questions."""
    try:
        logger.info(f"Querying medical RAG engine: '{request.query}'")
        result = await run_in_threadpool(rag_engine.query_guidelines, request.query, top_k=request.top_k)
        return result
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve medical guidelines.")
