import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from pydantic import BaseModel
from src.core.auth import get_current_user
from src.repositories.sprint1_repo import document_repository
from src.repositories.sprint2_repo import memory_repository, timeline_repository
from src.services.ai_contracts.docs_service import MockDocumentOCRService

router = APIRouter(prefix="/documents", tags=["Smart Document Analyzer"])
ocr_service = MockDocumentOCRService()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


class DocumentAnalysisResponse(BaseModel):
    document_id: str
    document_type: str
    status: str
    extracted_information: Dict[str, Any]
    warnings: list
    confidence: Optional[float] = None


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """
    Accepts supported medical documents and validates file type.
    """
    filename = file.filename or "unknown.pdf"
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    doc_record = {
        "document_id": doc_id,
        "patient_id": current_user,
        "filename": filename,
        "file_type": "pdf" if ext == ".pdf" else "image",
        "document_type": "prescription" if "presc" in filename.lower() else "lab_report",
        "status": "uploaded",
        "extracted_information": {},
        "warnings": [],
        "confidence": None,
    }
    saved = await document_repository.save_document(doc_record)
    return saved


@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Triggers AI OCR document analysis service contract and updates document record.
    Automatically integrates result into CarePath Memory & Patient Timeline.
    """
    doc = await document_repository.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{document_id}' not found.")

    await document_repository.update_status(document_id, "processing")

    ocr_result = await ocr_service.extract_medical_report(doc.get("filename", "report.pdf"))

    structured_result = {
        "document_type": ocr_result.get("document_type", "lab_report"),
        "extracted_information": ocr_result.get("extracted_values", {}),
        "warnings": [],
        "confidence": 0.95,
    }

    updated = await document_repository.update_status(document_id, "completed", result=structured_result)

    # ── Sprint 3 Integration: Store into Memory & Timeline ────────────────────
    patient_id = doc.get("patient_id", current_user)
    await memory_repository.store_context(patient_id, {
        "event_type": "DOCUMENT_ANALYSIS",
        "document_id": document_id,
        "document_type": structured_result["document_type"],
        "extracted_values": structured_result["extracted_information"]
    })

    await timeline_repository.add_event(patient_id, {
        "event_type": "REPORT_UPLOADED",
        "description": f"Processed {structured_result['document_type']} ({doc.get('filename')}).",
        "source": "Smart Document Analyzer"
    })

    return updated


@router.get("/{document_id}", response_model=DocumentAnalysisResponse)
async def get_document_details(
    document_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves full structured document analysis output.
    """
    doc = await document_repository.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{document_id}' not found.")
    return doc


@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Fast status poll endpoint for processing state.
    """
    doc = await document_repository.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{document_id}' not found.")
    return {"document_id": document_id, "status": doc.get("status", "unknown")}
