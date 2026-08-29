"""Clinical NLP API Endpoint."""
from fastapi import APIRouter, HTTPException, status, Body
from starlette.concurrency import run_in_threadpool
from app.schemas.nlp import BioNERResult
from app.services.nlp_engine import nlp_engine
from app.core.logging import logger

router = APIRouter(prefix="/nlp", tags=["Clinical Bio-NER"])


@router.post("/extract", response_model=BioNERResult, summary="Extract medical entities, symptoms, and ICD-10 codes from clinical text")
async def extract_clinical_entities(
    text: str = Body(..., embed=True, examples=["Patient presents with cough, fever, and shortness of breath for 3 days. Denies chest pain. Diagnosed with pneumonia."])
):
    """Parse unstructured clinical notes to extract structured medical concepts."""
    try:
        logger.info(f"Extracting clinical entities from text sample (length: {len(text)})")
        result = await run_in_threadpool(nlp_engine.extract_entities, text)
        return result
    except Exception as e:
        logger.error(f"Bio-NER extraction error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process clinical entity extraction.")
