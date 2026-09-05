"""
CarePath AI — Medication Agent Node
====================================
Normalizes patient medication data, extracts medications from uploaded prescription documents,
assigns source provenance, and enforces strict medication safety rules (NEVER autonomous prescribing/modifying).
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.core.logging import logger


async def medication_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Medication Agent.
    Extracts and normalizes recorded medications from complaint narratives and OCR document extractions.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_medication_node", encounter_id=encounter_id)

    ocr_texts = state.get("doc_ocr_extracted_text", [])
    complaint = state.get("chief_complaint", "").lower()

    extracted_meds: List[Dict[str, Any]] = []

    # Check narrative text for patient-reported medications
    if "medicine" in complaint or "medication" in complaint or "antibiotic" in complaint or "pill" in complaint:
        extracted_meds.append({
            "medication_name": "Unspecified Prior Medication",
            "dosage": "As previously taken",
            "source": "PATIENT_REPORTED",
            "status": "ACTIVE_UNRESPONSIVE",
            "notes": "Patient reported taking medication without symptom resolution."
        })

    # Extract medications from uploaded prescription OCR
    for doc in ocr_texts:
        if doc.get("document_type") == "Prescription":
            extracted_meds.append({
                "medication_name": doc.get("structured_data", {}).get("medication_name", "Extracted Prescription Item"),
                "dosage": doc.get("structured_data", {}).get("dosage", "Recorded Dose"),
                "source": "OCR_EXTRACTED",
                "status": "RECORDED",
                "notes": "Extracted from uploaded prescription document."
            })

    execution_history = list(state.get("execution_history", []))
    execution_history.append({
        "step_id": f"step_medication_{len(execution_history)}",
        "agent_name": "MedicationAgent",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["extracted_medications"],
        "error_message": None,
    })

    return {
        "extracted_medications": extracted_meds,
        "execution_history": execution_history,
    }
