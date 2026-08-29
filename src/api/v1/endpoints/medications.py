from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.core.auth import get_current_user
from src.repositories.sprint1_repo import medication_repository
from src.services.ai_contracts.medication_service import MockMedicationExtractionService

router = APIRouter(prefix="/medications", tags=["Medication Companion Foundation"])
med_service = MockMedicationExtractionService()


class MedicationExtractRequest(BaseModel):
    prescription_text: str
    patient_id: Optional[str] = None


class ScheduleRequest(BaseModel):
    reminder_times: List[str]
    start_date: str
    end_date: Optional[str] = None


class ActionReasonRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/extract", status_code=status.HTTP_201_CREATED)
async def extract_medications(
    payload: MedicationExtractRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Extracts structured medication information from prescription text.
    AI MUST NOT PRESCRIBE, MODIFY, STOP, OR CHANGE MEDICATION.
    """
    patient_id = payload.patient_id or current_user
    extracted = await med_service.extract_medications(payload.prescription_text)

    saved_items = []
    for item in extracted:
        item["patient_id"] = patient_id
        saved = await medication_repository.save_medication(item)
        saved_items.append(saved)

    return {"patient_id": patient_id, "medications": saved_items}


@router.get("")
async def list_medications(
    patient_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """
    Lists extracted/confirmed medications for the patient.
    """
    pid = patient_id or current_user
    meds = await medication_repository.list_medications(pid)
    return {"patient_id": pid, "medications": meds}


@router.get("/{medication_id}")
async def get_medication_detail(
    medication_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves specific medication details.
    """
    med = await medication_repository.get_medication(medication_id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Medication '{medication_id}' not found.")
    return med


@router.post("/{medication_id}/confirm")
async def confirm_medication(
    medication_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Patient verification step for extracted prescription details.
    """
    confirmed = await medication_repository.confirm_medication(medication_id)
    if not confirmed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Medication '{medication_id}' not found.")
    return {"status": "SUCCESS", "message": "Medication details confirmed by patient.", "medication": confirmed}


@router.post("/{medication_id}/schedule")
async def schedule_medication(
    medication_id: str,
    payload: ScheduleRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Sets reminder times and schedule parameters for medication.
    """
    sched = await medication_repository.set_schedule(medication_id, payload.dict())
    if not sched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Medication '{medication_id}' not found.")
    return {"status": "SUCCESS", "message": "Medication schedule updated.", "medication": sched}


@router.post("/{medication_id}/taken")
async def mark_medication_taken(
    medication_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Logs dosage taken event.
    """
    logged = await medication_repository.log_action(medication_id, "TAKEN")
    if not logged:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Medication '{medication_id}' not found.")
    return {"status": "SUCCESS", "message": "Dose logged as TAKEN.", "medication": logged}


@router.post("/{medication_id}/skipped")
async def mark_medication_skipped(
    medication_id: str,
    payload: ActionReasonRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Logs dosage skipped event with optional reason.
    """
    logged = await medication_repository.log_action(medication_id, "SKIPPED", reason=payload.reason)
    if not logged:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Medication '{medication_id}' not found.")
    return {"status": "SUCCESS", "message": "Dose logged as SKIPPED.", "medication": logged}
