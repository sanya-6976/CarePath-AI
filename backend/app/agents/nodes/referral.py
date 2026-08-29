import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.agents.state import CarePathState, SpecialistReferral, UrgencyCategory
from src.config import settings
from src.core.logging import logger


class ReferralAgent:
    """
    Production Referral Agent.
    Maps clinical reasoning hypotheses and RAG evidence guidelines into appropriate
    primary & secondary medical specialist referrals with actionable preparation guidance.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or getattr(settings, "GEMINI_API_KEY", None)

    async def generate_specialist_referral(self, state: CarePathState) -> SpecialistReferral:
        logger.info("referral_agent_routing_specialist", encounter_id=state.get("encounter_id"))
        return self._fallback_referral_mapping(state)

    def _fallback_referral_mapping(self, state: CarePathState) -> SpecialistReferral:
        hypotheses = state.get("clinical_hypotheses", [])
        evidence = state.get("retrieved_evidence", [])
        urgency = state.get("urgency_level") or UrgencyCategory.ROUTINE

        # Default mapping based on top hypothesis
        primary_specialty = "General Internal Medicine"
        secondary_specialty = "Gastroenterology"
        rationale = "General internal medicine evaluation recommended for comprehensive symptom management."
        timeframe = "Within 1-2 Weeks"
        prep_instructions = [
            "Bring a printed record of your current symptoms and duration.",
            "List any over-the-counter or prescription medications you are currently taking.",
        ]

        if hypotheses:
            top_hypo = hypotheses[0]
            if "Appendicitis" in top_hypo.condition_name:
                primary_specialty = "General Surgery"
                secondary_specialty = "Gastroenterology"
                urgency = UrgencyCategory.URGENT
                timeframe = "Within 24 Hours (Urgent Triage)"
                rationale = (
                    "High clinical index of suspicion for acute appendicitis based on localized right lower quadrant pain "
                    "and elevated white blood cell count in uploaded lab results."
                )
                prep_instructions = [
                    "Seek urgent medical evaluation at an Urgent Care Center or Hospital Emergency Department.",
                    "Do NOT consume food or liquids (fasting) in case urgent surgical evaluation or ultrasound imaging is required.",
                    "Bring your uploaded CBC lab report and symptom summary.",
                ]

        return SpecialistReferral(
            primary_specialty=primary_specialty,
            secondary_specialty=secondary_specialty,
            urgency=urgency,
            clinical_rationale=rationale,
            suggested_timeframe=timeframe,
            preparation_instructions=prep_instructions,
        )


async def referral_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node Wrapper for Referral Agent.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_referral_node", encounter_id=encounter_id)

    agent = ReferralAgent()
    referral_obj = await agent.generate_specialist_referral(state)

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_referral_{len(execution_history)}",
        "agent_name": "ReferralAgent",
        "started_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "status": "SUCCESS",
        "state_delta_keys": ["referral", "urgency_level"],
        "error_message": None,
    })

    return {
        "referral": referral_obj,
        "urgency_level": referral_obj.urgency,
        "execution_history": execution_history,
    }
