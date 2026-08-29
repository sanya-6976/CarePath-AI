import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.agents.state import CarePathState, TimelineEvent
from src.config import settings
from src.core.logging import logger


class TimelineAgent:
    """
    Production Timeline Agent.
    Synthesizes symptoms, onset durations, lab report events, and vision findings
    into a unified chronological patient history graph.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or settings.GEMINI_API_KEY

    async def construct_patient_timeline(self, state: CarePathState) -> List[TimelineEvent]:
        logger.info("timeline_agent_constructing_chronology", encounter_id=state.get("encounter_id"))
        
        events: List[TimelineEvent] = []

        # The medical router injects only this patient's persisted updates into
        # state. Include them before current inputs so the agent's chronology is
        # genuinely longitudinal, rather than reconstructing a current-only view.
        for historical in state.get("historical_context", []):
            content = str(historical.get("content", "")).strip()
            if content:
                events.append(TimelineEvent(
                    event_id=f"evt_history_{len(events)}",
                    timestamp_description=historical.get("date") or "Prior CarePath update",
                    event_type=str(historical.get("type") or "PATIENT_UPDATE").upper(),
                    description=content,
                    source_agent="LongitudinalContext",
                ))

        # 1. Add Chief Complaint Onset Event
        duration = state.get("symptoms_duration") or "Initial Onset"
        complaint = state.get("chief_complaint", "")
        events.append(
            TimelineEvent(
                event_id=f"evt_complaint_{len(events)}",
                timestamp_description=f"Onset: {duration}",
                event_type="SYMPTOM",
                description=f"Primary Chief Complaint reported: '{complaint}'",
                source_agent="IntakeAgent",
            )
        )

        # 2. Add Vision Analysis Events
        for v_res in state.get("vision_results", []):
            findings_str = "; ".join(v_res.visual_findings)
            events.append(
                TimelineEvent(
                    event_id=f"evt_vision_{len(events)}",
                    timestamp_description="Current Evaluation",
                    event_type="IMAGE_FINDING",
                    description=f"Visual Inspection Findings: {findings_str}",
                    source_agent="VisionAgent",
                )
            )

        # 3. Add OCR Lab Report Events
        for o_res in state.get("ocr_results", []):
            events.append(
                TimelineEvent(
                    event_id=f"evt_ocr_{len(events)}",
                    timestamp_description="Uploaded Document Record",
                    event_type="LAB_TEST",
                    description=f"Document '{o_res.document_type}': {o_res.extracted_text}",
                    source_agent="MedicalDocsAgent",
                )
            )

        return events


async def timeline_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node Wrapper for Timeline Agent.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_timeline_node", encounter_id=encounter_id)

    agent = TimelineAgent()
    timeline_events = await agent.construct_patient_timeline(state)

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_timeline_{len(execution_history)}",
        "agent_name": "TimelineAgent",
        "started_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "status": "SUCCESS",
        "state_delta_keys": ["patient_timeline"],
        "error_message": None,
    })

    return {
        "patient_timeline": timeline_events,
        "execution_history": execution_history,
    }
