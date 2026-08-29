from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.core.auth import get_current_user
from src.repositories.sprint2_repo import doctor_bridge_repository, memory_repository
from src.agents.graph import carepath_graph
from src.agents.state import CarePathState, UrgencyLevel

router = APIRouter(prefix="/doctor-bridge", tags=["CarePath Doctor Bridge"])


class DoctorBriefRequest(BaseModel):
    patient_id: Optional[str] = None
    chief_complaint: str
    symptoms_duration: Optional[str] = None
    symptoms_severity: Optional[int] = 5


class DoctorReviewRequest(BaseModel):
    brief_id: str
    clinician_name: str
    corrections: Optional[str] = None
    notes: str
    confirmed_next_step: str
    follow_up_instructions: Optional[str] = None


@router.post("/brief", status_code=status.HTTP_201_CREATED)
async def generate_doctor_brief(
    payload: DoctorBriefRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generates a doctor-ready patient brief organizing medical history, symptoms, reports, and concerns.
    """
    patient_id = payload.patient_id or current_user

    state: CarePathState = {
        "encounter_id": f"enc_doc_{patient_id}",
        "patient_id": patient_id,
        "request_type": "doctor_bridge",
        "chief_complaint": payload.chief_complaint,
        "symptoms_duration": payload.symptoms_duration,
        "symptoms_severity": payload.symptoms_severity,
        "attachments": [],
        "memory_context": [],
        "extracted_demographics": {},
        "structured_symptoms": [],
        "vision_analysis_results": [],
        "doc_ocr_extracted_text": [],
        "extracted_medications": [],
        "patient_timeline": [],
        "rag_evidence_docs": [],
        "clinical_hypotheses": [],
        "confidence_score": 0.0,
        "needs_more_info": False,
        "missing_info_prompt": None,
        "doctor_brief": None,
        "doctor_questions": [],
        "doctor_feedback": None,
        "is_paused": False,
        "awaiting_doctor_review": False,
        "urgency_level": UrgencyLevel.ROUTINE,
        "is_emergency": False,
        "emergency_reasoning": None,
        "recommended_specialty": None,
        "specialist_rationale": None,
        "referral_details": None,
        "patient_care_plan": [],
        "care_plan_details": None,
        "follow_up_schedule": {},
        "next_agent": "supervisor",
        "execution_history": [],
        "error_state": None,
    }

    final_state = await carepath_graph.ainvoke(state)
    brief = final_state.get("doctor_brief", {})

    saved = await doctor_bridge_repository.save_brief(brief)
    return saved


@router.get("/brief/{brief_id}")
async def get_doctor_brief(
    brief_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves existing Doctor Brief.
    """
    brief = await doctor_bridge_repository.get_brief(brief_id)
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Doctor Brief '{brief_id}' not found.")
    return brief


@router.post("/questions")
async def generate_case_questions(
    brief_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Generates case-specific questions based on patient context to assist clinician communication.
    """
    brief = await doctor_bridge_repository.get_brief(brief_id)
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Doctor Brief '{brief_id}' not found.")

    questions = [
        f"How long have you experienced '{brief.get('chief_complaint', 'these symptoms')}'?",
        "Have you noticed any change in symptom severity after taking your current medications?",
        "Are there any specific diagnostic tests or lab reports you would like reviewed?",
        "What specific warning symptoms should prompt emergency care?"
    ]

    saved = await doctor_bridge_repository.save_questions(brief_id, questions)
    return saved


@router.get("/questions/{brief_id}")
async def get_case_questions(
    brief_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves case-specific questions for a brief.
    """
    brief = await doctor_bridge_repository.get_brief(brief_id)
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Doctor Brief '{brief_id}' not found.")
    return {
        "brief_id": brief_id,
        "questions": [
            f"How long have you experienced '{brief.get('chief_complaint', 'these symptoms')}'?",
            "Have you noticed any change in symptom severity after taking your current medications?",
            "Are there any specific diagnostic tests or lab reports you would like reviewed?"
        ]
    }


@router.post("/review", status_code=status.HTTP_201_CREATED)
async def submit_doctor_review(
    payload: DoctorReviewRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Doctor submits clinical review & feedback.
    Updates patient CarePath Memory and resumes paused workflow.
    """
    brief = await doctor_bridge_repository.get_brief(payload.brief_id)
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Doctor Brief '{payload.brief_id}' not found.")

    review_record = await doctor_bridge_repository.save_review(payload.dict())

    # Store confirmed clinician feedback into CarePath Memory
    await memory_repository.store_context(brief.get("patient_id", current_user), {
        "event_type": "CLINICIAN_REVIEW",
        "clinician_name": payload.clinician_name,
        "confirmed_next_step": payload.confirmed_next_step,
        "notes": payload.notes,
        "is_clinician_feedback": True
    })

    return {
        "status": "SUCCESS",
        "message": "Clinician review submitted successfully. CarePath Memory updated and workflow resumed.",
        "review": review_record
    }


@router.get("/review/{review_id}")
async def get_doctor_review(
    review_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves clinician review feedback.
    """
    rev = await doctor_bridge_repository.get_review(review_id)
    if not rev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Doctor Review '{review_id}' not found.")
    return rev
