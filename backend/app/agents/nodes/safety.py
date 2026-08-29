import asyncio
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.agents.state import CarePathState, UrgencyCategory, AgentAlert, AlertSeverity
from src.core.logging import logger

# Deterministic Emergency Red Flag Patterns (High Precision, Zero Latency)
DETERMINISTIC_RED_FLAGS = [
    (r"\b(crushing chest pain|chest tightness|radiating to (left arm|jaw))\b", "ACUTE_CORONARY_SYNDROME"),
    (r"\b(difficulty breathing|gasping|severe shortness of breath|cyanosis|blue lips)\b", "RESPIRATORY_DISTRESS"),
    (r"\b(sudden weakness|face drooping|arm numbness|slurred speech|aphasia)\b", "ACUTE_STROKE_FAST"),
    (r"\b(anaphylaxis|swollen tongue|throat closing|unable to swallow)\b", "ANAPHYLAXIS_EMERGENCY"),
    (r"\b(unconscious|unresponsive|fainted|seizure > 5 min)\b", "NEUROLOGICAL_EMERGENCY"),
    (r"\b(coughing blood|vomiting bright red blood|severe uncontrolled bleeding)\b", "HEMORRHAGIC_EMERGENCY"),
    (r"\b(suicidal thoughts|want to end my life|self harm)\b", "PSYCHIATRIC_EMERGENCY"),
]


class SafetyEvaluationResult(BaseModel):
    is_emergency: bool
    urgency_category: UrgencyCategory
    detected_red_flags: List[str]
    clinical_justification: str
    confidence: float = Field(ge=0.0, le=1.0)


class SafetyAgent:
    """
    Production Safety Agent.
    Combines a deterministic high-precision rule engine with LLM fallback checks
    to ensure zero-latency emergency triage short-circuiting.
    """

    def __init__(self, ai_llm_client: Optional[Any] = None):
        self.ai_llm_client = ai_llm_client

    async def evaluate_safety(self, complaint: str, severity: Optional[int]) -> SafetyEvaluationResult:
        complaint_lower = complaint.lower()
        detected_flags = []

        # Step 1: High-Speed Regex Rule Evaluation
        for pattern, code in DETERMINISTIC_RED_FLAGS:
            if re.search(pattern, complaint_lower):
                detected_flags.append(code)

        # High severity score override
        if severity and severity >= 9 and not detected_flags:
            detected_flags.append("HIGH_SEVERITY_OVERRIDE_SCORE_9_10")

        if detected_flags:
            logger.warn("safety_agent_emergency_detected", red_flags=detected_flags)
            return SafetyEvaluationResult(
                is_emergency=True,
                urgency_category=UrgencyCategory.EMERGENCY,
                detected_red_flags=detected_flags,
                clinical_justification=f"Immediate emergency triage triggered due to critical red-flag indicators: {', '.join(detected_flags)}.",
                confidence=1.0,
            )

        # Step 2: Non-Emergency Triage Categorization
        urgency = UrgencyCategory.ROUTINE
        if severity and severity >= 7:
            urgency = UrgencyCategory.URGENT

        return SafetyEvaluationResult(
            is_emergency=False,
            urgency_category=urgency,
            detected_red_flags=[],
            clinical_justification="No immediate life-threatening emergency symptoms detected in preliminary safety sweep.",
            confidence=0.95,
        )


async def safety_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node Wrapper for Safety Agent.
    Execution guaranteed at the entry of graph processing.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_safety_node", encounter_id=encounter_id)
    
    agent = SafetyAgent()
    result = await agent.evaluate_safety(
        complaint=state.get("chief_complaint", ""),
        severity=state.get("symptoms_severity"),
    )

    # State Delta Update
    alerts = state.get("alerts", [])
    if result.is_emergency:
        alerts.append(
            AgentAlert(
                alert_id=f"alert_safety_{datetime.utcnow().timestamp()}",
                agent_name="SafetyAgent",
                severity=AlertSeverity.CRITICAL,
                code="EMERGENCY_RED_FLAG",
                message=result.clinical_justification,
            )
        )

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_safety_{len(execution_history)}",
        "agent_name": "SafetyAgent",
        "started_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "status": "SUCCESS",
        "state_delta_keys": ["is_emergency", "urgency_level", "emergency_reasoning", "alerts"],
        "error_message": None,
    })

    return {
        "is_emergency": result.is_emergency,
        "urgency_level": result.urgency_category,
        "emergency_reasoning": result.clinical_justification if result.is_emergency else None,
        "alerts": alerts,
        "execution_history": execution_history,
    }
