from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.services.ai_contracts.medication_service import MockMedicationExtractionService
from src.core.logging import logger

medication_ai_service = MockMedicationExtractionService()


async def medication_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Medication Companion Agent.
    Extracts structured medication information from prescription text/OCR.
    Safety rule: Never prescribes, modifies, or alters medication.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_medication_node", encounter_id=encounter_id)

    ocr_texts = state.get("doc_ocr_extracted_text", [])
    chief_complaint = state.get("chief_complaint", "")

    source_text = chief_complaint
    if ocr_texts:
        source_text += "\n" + "\n".join([t.get("extracted_text", "") for t in ocr_texts])

    extracted_meds = await medication_ai_service.extract_medications(source_text)

    history = state.get("execution_history", [])
    history.append({
        "step_id": f"step_medication_{len(history)}",
        "agent_name": "MedicationAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["extracted_medications"],
        "error_message": None,
    })

    return {
        "extracted_medications": extracted_meds,
        "execution_history": history,
    }
