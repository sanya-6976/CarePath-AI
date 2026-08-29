from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.core.auth import get_current_user
from src.repositories.sprint2_repo import care_plan_repository
from src.agents.graph import carepath_graph
from src.agents.state import CarePathState, UrgencyLevel

router = APIRouter(prefix="/care-plans", tags=["Personalized Care Plan Workflow"])


class CarePlanGenerateRequest(BaseModel):
    patient_id: Optional[str] = None
    chief_complaint: str
    recommended_specialty: Optional[str] = None
    doctor_notes: Optional[str] = None


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_care_plan(
    payload: CarePlanGenerateRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Generates personalized care plan organizing patient next steps.
    Strictly separates AI-generated guidance from Clinician-provided instructions.
    """
    patient_id = payload.patient_id or current_user

    doctor_feedback = None
    if payload.doctor_notes:
        doctor_feedback = {
            "notes": payload.doctor_notes,
            "confirmed_next_step": "Follow up as specified by doctor."
        }

    state: CarePathState = {
        "encounter_id": f"enc_cp_{patient_id}",
        "patient_id": patient_id,
        "request_type": "care_plan",
        "chief_complaint": payload.chief_complaint,
        "symptoms_duration": None,
        "symptoms_severity": 5,
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
        "doctor_feedback": doctor_feedback,
        "is_paused": False,
        "awaiting_doctor_review": False,
        "urgency_level": UrgencyLevel.ROUTINE,
        "is_emergency": False,
        "emergency_reasoning": None,
        "recommended_specialty": payload.recommended_specialty,
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
    plan_details = final_state.get("care_plan_details", {})

    saved = await care_plan_repository.save_care_plan(plan_details)
    return saved


@router.get("/{care_plan_id}")
async def get_care_plan_details(
    care_plan_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves specific care plan details.
    """
    plan = await care_plan_repository.get_care_plan(care_plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Care Plan '{care_plan_id}' not found.")
    return plan
