from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.core.logging import logger


async def timeline_node(state: CarePathState) -> Dict[str, Any]:
    """LangGraph Node — Patient Timeline Builder."""
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_timeline_node", encounter_id=encounter_id)

    events: List[Dict[str, Any]] = []

    for historical in state.get("historical_context", []):
        content = str(historical.get("content", "")).strip()
        if content:
            events.append({
                "event_id": f"evt_history_{len(events)}",
                "timestamp_description": historical.get("date") or "Prior CarePath update",
                "event_type": str(historical.get("type") or "PATIENT_UPDATE").upper(),
                "description": content,
                "source_agent": "LongitudinalContext",
            })

    # Chief complaint onset event
    events.append({
        "event_id": "evt_complaint_0",
        "timestamp_description": f"Onset: {state.get('symptoms_duration', 'Unknown')}",
        "event_type": "SYMPTOM",
        "description": f"Chief Complaint: {state.get('chief_complaint', '')}",
        "source_agent": "IntakeAgent",
    })

    # Vision findings
    for i, v in enumerate(state.get("vision_analysis_results", [])):
        events.append({
            "event_id": f"evt_vision_{i}",
            "timestamp_description": "Current Evaluation",
            "event_type": "IMAGE_FINDING",
            "description": f"Visual findings: {v.get('findings', [])}",
            "source_agent": "VisionAgent",
        })

    # OCR lab events
    for i, o in enumerate(state.get("doc_ocr_extracted_text", [])):
        events.append({
            "event_id": f"evt_ocr_{i}",
            "timestamp_description": "Uploaded Document",
            "event_type": "LAB_TEST",
            "description": f"{o.get('document_type', 'Document')}: {o.get('extracted_text', '')}",
            "source_agent": "MedicalDocsAgent",
        })

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_timeline_{len(execution_history)}",
        "agent_name": "TimelineAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["patient_timeline"],
        "error_message": None,
    })

    return {
        "patient_timeline": events,
        "execution_history": execution_history,
    }
