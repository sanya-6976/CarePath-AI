from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger


async def clinical_reasoning_node(state: CarePathState) -> Dict[str, Any]:
    """LangGraph Node — Clinical Reasoning & Differential Hypothesis Agent."""
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_clinical_reasoning_node", encounter_id=encounter_id)

    complaint = state.get("chief_complaint", "").lower()
    ocr_results = state.get("doc_ocr_extracted_text", [])

    # Detect elevated WBC from OCR
    high_wbc = any(
        r.get("structured_data", {}).get("WBC", {}).get("flag") == "HIGH"
        for r in ocr_results
    )

    hypotheses: List[Dict[str, Any]] = []
    confidence = 0.85

    if any(kw in complaint for kw in ["abdominal", "stomach", "right lower", "rlq"]):
        hypotheses.append({
            "hypothesis_id": "hypo_appendicitis_01",
            "condition_name": "Suspected Acute Appendicitis",
            "rationale": "RLQ pain with acute onset and leukocytosis.",
            "likelihood_score": 0.88 if high_wbc else 0.72,
            "key_supporting_factors": [
                "Right lower abdominal pain",
                "Leukocytosis (High WBC)" if high_wbc else "Acute onset",
            ],
            "key_opposing_factors": ["No high-grade fever reported"],
        })
        hypotheses.append({
            "hypothesis_id": "hypo_gastroenteritis_02",
            "condition_name": "Acute Gastroenteritis",
            "rationale": "Abdominal discomfort with GI inflammation.",
            "likelihood_score": 0.45,
            "key_supporting_factors": ["Abdominal pain"],
            "key_opposing_factors": ["Localized RLQ pattern"],
        })
    else:
        hypotheses.append({
            "hypothesis_id": "hypo_general_eval_00",
            "condition_name": "Unspecified Presentation",
            "rationale": "Requires comprehensive physical examination.",
            "likelihood_score": 0.60,
            "key_supporting_factors": ["Reported complaint"],
        })
        confidence = 0.55

    needs_more_info = confidence < 0.60

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_reasoning_{len(execution_history)}",
        "agent_name": "ClinicalReasoningAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["clinical_hypotheses", "confidence_score", "needs_more_info"],
        "error_message": None,
    })

    return {
        "clinical_hypotheses": hypotheses,
        "confidence_score": confidence,
        "needs_more_info": needs_more_info,
        "missing_info_prompt": (
            "Please specify any fever, nausea, or localized tenderness."
            if needs_more_info else None
        ),
        "execution_history": execution_history,
    }
