import asyncio
import uuid
import json
from typing import AsyncGenerator
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse
from src.agents.graph import carepath_graph
from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger
from src.schemas.encounter_schema import (
    EncounterCreateRequest,
    EncounterResponse,
    ProcessEncounterResponse,
)

router = APIRouter(prefix="/encounters", tags=["Patient Encounters & Triage"])

ENCOUNTER_SESSIONS: dict = {}


@router.post("", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_encounter(payload: EncounterCreateRequest):
    """
    Initializes a new patient navigation session.
    """
    encounter_id = f"enc_{uuid.uuid4().hex[:12]}"
    patient_id = f"pat_{uuid.uuid4().hex[:8]}"

    initial_state: CarePathState = {
        "encounter_id": encounter_id,
        "patient_id": patient_id,
        "request_type": "encounter",
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

    ENCOUNTER_SESSIONS[encounter_id] = initial_state
    logger.info("encounter_created", encounter_id=encounter_id)

    return EncounterResponse(
        encounter_id=encounter_id,
        patient_id=patient_id,
        status="INITIALIZED",
        chief_complaint=payload.chief_complaint,
        symptoms_duration=payload.symptoms_duration,
        symptoms_severity=payload.symptoms_severity,
    )


@router.post("/{encounter_id}/process", response_model=ProcessEncounterResponse)
async def process_encounter(encounter_id: str, background_tasks: BackgroundTasks):
    """
    Triggers the LangGraph multi-agent processing pipeline asynchronously.
    """
    if encounter_id not in ENCOUNTER_SESSIONS:
        raise HTTPException(status_code=404, detail="Encounter session not found.")

    logger.info("triggering_agent_graph_execution", encounter_id=encounter_id)

    async def run_graph():
        state = ENCOUNTER_SESSIONS[encounter_id]
        final_state = await carepath_graph.ainvoke(state)
        ENCOUNTER_SESSIONS[encounter_id] = final_state
        logger.info("agent_graph_execution_finished", encounter_id=encounter_id)

    background_tasks.add_task(run_graph)

    return ProcessEncounterResponse(
        encounter_id=encounter_id,
        status="PROCESSING",
        message="CarePath multi-agent graph execution started.",
        stream_url=f"/api/v1/encounters/{encounter_id}/stream",
    )


@router.get("/{encounter_id}/stream")
async def stream_encounter_progress(encounter_id: str):
    """
    Server-Sent Events (SSE) streaming endpoint emitting unified workflow events.
    Events: workflow_started, agent_started, agent_completed, doctor_review_required, workflow_completed, workflow_failed.
    """
    if encounter_id not in ENCOUNTER_SESSIONS:
        raise HTTPException(status_code=404, detail="Encounter session not found.")

    async def event_generator() -> AsyncGenerator[str, None]:
        history_cursor = 0
        yield f"event: workflow_started\ndata: {json.dumps({'encounter_id': encounter_id, 'status': 'STARTED'})}\n\n"

        while True:
            state = ENCOUNTER_SESSIONS.get(encounter_id, {})
            history = state.get("execution_history", [])

            while history_cursor < len(history):
                step = history[history_cursor]
                agent_name = step["agent_name"]
                event_name = "agent_completed"

                if agent_name == "DoctorBridgeAgent" and step["status"] == "PAUSED_FOR_DOCTOR_REVIEW":
                    event_name = "doctor_review_required"
                elif agent_name == "DocsAgent":
                    event_name = "document_analyzed"
                elif agent_name == "EvidenceAgent":
                    event_name = "evidence_retrieved"
                elif agent_name == "ReferralAgent":
                    event_name = "referral_generated"
                elif agent_name == "CarePlanAgent":
                    event_name = "care_plan_generated"

                payload = json.dumps({
                    "encounter_id": encounter_id,
                    "agent_name": agent_name,
                    "status": step["status"],
                    "summary": step.get("output_summary", ""),
                })
                yield f"event: {event_name}\ndata: {payload}\n\n"
                history_cursor += 1

            if state.get("is_paused") or state.get("awaiting_doctor_review"):
                payload = json.dumps({
                    "encounter_id": encounter_id,
                    "status": "PAUSED_FOR_DOCTOR_REVIEW",
                    "message": "Workflow paused awaiting clinician feedback."
                })
                yield f"event: doctor_review_required\ndata: {payload}\n\n"
                break

            if state.get("recommended_specialty") or state.get("is_emergency") or state.get("patient_care_plan"):
                payload = json.dumps({
                    "encounter_id": encounter_id,
                    "status": "FINISHED",
                    "urgency": str(state.get("urgency_level")),
                })
                yield f"event: workflow_completed\ndata: {payload}\n\n"
                break

            if state.get("error_state"):
                payload = json.dumps({
                    "encounter_id": encounter_id,
                    "status": "FAILED",
                    "error": state.get("error_state"),
                })
                yield f"event: workflow_failed\ndata: {payload}\n\n"
                break

            await asyncio.sleep(0.2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
