from abc import ABC, abstractmethod
from typing import Any, Dict, List
from src.services.ai_contracts.base_ai import BaseAIService


class IVisionAIService(BaseAIService):
    """
    Contract interface for AI Teammate responsible for Computer Vision models.
    """

    @abstractmethod
    async def analyze_medical_image(
        self, image_url_or_path: str, image_type: str
    ) -> Dict[str, Any]:
        """
        Analyzes a medical image (e.g., skin lesion, X-ray, rash) and returns structured findings.
        """
        pass


class MockVisionAIService(IVisionAIService):
    """
    Mock implementation used for backend unit testing & local development
    prior to receiving production computer vision models from the AI teammate.
    """

    async def check_health(self) -> bool:
        return True

    async def analyze_medical_image(
        self, image_url_or_path: str, image_type: str
    ) -> Dict[str, Any]:
        return {
            "findings": [
                "Localised erythematous macular rash on lower leg",
                "No signs of deep tissue ulceration or necrosis",
            ],
            "confidence": 0.88,
            "detected_abnormalities": ["erythema", "dermal_inflammation"],
            "suggested_specialties": ["Dermatology"],
        }
