"""
CarePath AI — Extensible AI Provider Abstraction Layer
======================================================
Provides an abstract base class `AIProvider` and concrete implementations for:
- `GeminiProvider`: Primary contextual reasoning and care navigation synthesis.
- `GroqReviewerProvider`: Independent clinical consistency, safety, and contradiction reviewer.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.ai_client import generate_gemini_json
from app.core.groq_client import review_with_groq
from app.schemas.review_schema import GroqReviewResult
from app.core.logging import logger


class AIProvider(ABC):
    """Abstract Base Class for AI Model Providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generate structured reasoning or navigation content."""
        pass

    @abstractmethod
    async def review(self, patient_context: Dict[str, Any], proposed_navigation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform independent review of proposed navigation plan."""
        pass


class GeminiProvider(AIProvider):
    """Primary reasoning provider powered by Gemini 3.6 Flash."""

    async def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        logger.info("invoking_primary_gemini_provider")
        return await generate_gemini_json(prompt=prompt, system_instruction=system_instruction)

    async def review(self, patient_context: Dict[str, Any], proposed_navigation: Dict[str, Any]) -> Dict[str, Any]:
        # Gemini acts primarily as the synthesis model; return default pass if called for review
        return {"review_status": "pass", "provider": "gemini", "review_summary": "Gemini primary synthesis model."}


class GroqReviewerProvider(AIProvider):
    """Independent reviewer provider powered by Groq (llama-3.3-70b-versatile)."""

    async def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # Groq acts primarily as the reviewer model
        logger.info("invoking_groq_reviewer_provider_generate")
        return None

    async def review(self, patient_context: Dict[str, Any], proposed_navigation: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("invoking_groq_reviewer_provider_review")
        return await review_with_groq(patient_context=patient_context, proposed_navigation=proposed_navigation)
