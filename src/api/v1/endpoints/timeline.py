from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.core.auth import get_current_user
from src.repositories.sprint2_repo import timeline_repository

router = APIRouter(prefix="/timeline", tags=["AI-Generated Patient Timeline"])


class TimelineEventRequest(BaseModel):
    event_type: str
    description: str
    source: Optional[str] = "Patient input"


@router.get("/{patient_id}")
async def get_patient_timeline(
    patient_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves chronological patient timeline events.
    """
    events = await timeline_repository.get_events(patient_id)
    return {"patient_id": patient_id, "total_events": len(events), "timeline_events": events}


@router.get("/{patient_id}/summary")
async def get_timeline_summary(
    patient_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves high-level summary narrative of patient's timeline.
    """
    summary = await timeline_repository.get_summary(patient_id)
    return summary


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def add_timeline_event(
    payload: TimelineEventRequest,
    patient_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """
    Appends a new verified event to the patient timeline.
    """
    pid = patient_id or current_user
    created = await timeline_repository.add_event(pid, payload.dict())
    return {"status": "SUCCESS", "event": created}
