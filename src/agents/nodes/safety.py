import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger

# High-precision regex patterns for zero-latency emergency detection
EMERGENCY_PATTERNS = [
    (r"\b(crushing chest pain|chest tightness|radiating to (left arm|jaw))\b",    "ACUTE_CORONARY_SYNDROME"),
    (r"\b(shortness of breath|difficulty breathing|gasping|cyanosis|blue lips)\b", "RESPIRATORY_DISTRESS"),
    (r"\b(sudden weakness|face drooping|facial droop|slurred speech|aphasia)\b",   "ACUTE_STROKE_FAST"),
    (r"\b(anaphylaxis|throat closing|swollen tongue|unable to swallow)\b",         "ANAPHYLAXIS"),
    (r"\b(unconscious|unresponsive|fainted|seizure)\b",                            "NEUROLOGICAL_EMERGENCY"),
    (r"\b(coughing blood|vomiting blood|severe uncontrolled bleeding)\b",          "HEMORRHAGIC_EMERGENCY"),
    (r"\b(suicidal thoughts|want to end my life|self.?harm)\b",                    "PSYCHIATRIC_EMERGENCY"),
    # Simple keyword fallbacks kept for broad coverage
    (r"\b(stroke|heart attack|cardiac arrest|anaphylactic)\b",                    "CRITICAL_KEYWORD"),
]


async def safety_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Safety Agent.
    Regex-based emergency red-flag detection with severity score escalation.
    Short-circuits graph to immediate emergency guidance when triggered.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_safety_node", encounter_id=encounter_id)

    complaint = state.get("chief_complaint", "").lower()
    severity  = state.get("symptoms_severity")

    detected_flags: List[str] = []
    for pattern, code in EMERGENCY_PATTERNS:
        if re.search(pattern, complaint):
            detected_flags.append(code)

    # High severity score override when no keyword match found
    if not detected_flags and severity and severity >= 9:
        detected_flags.append("HIGH_SEVERITY_SCORE_9_10")

    is_emergency = bool(detected_flags)
    urgency      = UrgencyLevel.EMERGENCY if is_emergency else (
                   UrgencyLevel.URGENT   if severity and severity >= 7 else
                   UrgencyLevel.ROUTINE)

    if is_emergency:
        logger.warning("safety_emergency_short_circuit_triggered",
                       encounter_id=encounter_id, flags=detected_flags)

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id":          f"step_safety_{len(execution_history)}",
        "agent_name":       "SafetyAgent",
        "started_at":       datetime.now().isoformat(),
        "completed_at":     datetime.now().isoformat(),
        "status":           "SUCCESS",
        "state_delta_keys": ["is_emergency", "urgency_level", "emergency_reasoning"],
        "error_message":    None,
    })

    care_plan = state.get("patient_care_plan", [])
    if is_emergency and not care_plan:
        care_plan = [
            "CALL EMERGENCY SERVICES (911/112) IMMEDIATELY.",
            "Do not drive yourself to the hospital.",
            "Remain calm and still until emergency responders arrive.",
        ]

    return {
        "is_emergency":       is_emergency,
        "urgency_level":      urgency,
        "emergency_reasoning": (
            f"Critical red-flag indicators detected: {', '.join(detected_flags)}."
            if is_emergency else None
        ),
        "patient_care_plan":  care_plan,
        "execution_history":  execution_history,
    }
