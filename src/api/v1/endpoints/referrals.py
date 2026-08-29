from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.core.auth import get_current_user
from src.repositories.sprint2_repo import referral_repository
from src.agents.graph import carepath_graph
from src.agents.state import CarePathState, UrgencyLevel

router = APIRouter(prefix="/referrals", tags=["Explainable Referral Workflow"])


class ReferralRecommendRequest(BaseModel):
    patient_id: Optional[str] = None
    chief_complaint: str
    symptoms_duration: Optional[str] = None
    symptoms_severity: Optional[int] = 5


@router.post("/recommend", status_code=status.HTTP_201_CREATED)
async def recommend_referral(
    payload: ReferralRecommendRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Produces structured navigation recommendation based on symptoms, timeline, and RAG evidence.
    Mandatory Disclaimer: 'Navigation guidance, not a diagnosis.'
    """
    patient_id = payload.patient_id or current_user

    state: CarePathState = {
        "encounter_id": f"enc_ref_{patient_id}",
        "patient_id": patient_id,
        "request_type": "referral",
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
    ref_details = final_state.get("referral_details", {})

    if not ref_details:
        ref_details = {
            "referral_id": f"ref_{patient_id}",
            "specialist": final_state.get("recommended_specialty", "General Internal Medicine"),
            "reasoning": [final_state.get("specialist_rationale", "Based on symptom narrative.")],
            "supporting_evidence": [],
            "confidence": final_state.get("confidence_score", 0.85),
            "urgency": str(final_state.get("urgency_level", "ROUTINE")),
            "disclaimer": "Navigation guidance, not a diagnosis."
        }

    saved = await referral_repository.save_referral(ref_details)
    return saved


@router.get("/{referral_id}")
async def get_referral_details(
    referral_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves referral recommendation details.
    """
    ref = await referral_repository.get_referral(referral_id)
    if not ref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Referral '{referral_id}' not found.")
    return ref
