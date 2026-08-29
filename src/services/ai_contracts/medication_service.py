from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from src.services.ai_contracts.base_ai import BaseAIService


class IMedicationExtractionService(BaseAIService):
    """
    Contract interface for AI service extracting medication details from prescription text or documents.
    """

    @abstractmethod
    async def extract_medications(
        self, text_or_doc_url: str
    ) -> List[Dict[str, Any]]:
        """
        Extracts structured medication information from prescription text/document.
        Must NOT infer dosage if unstated; flags requires_confirmation if uncertain.
        """
        pass


class MockMedicationExtractionService(IMedicationExtractionService):
    """
    Mock implementation for unit testing and backend decoupling.
    """

    async def check_health(self) -> bool:
        return True

    async def extract_medications(
        self, text_or_doc_url: str
    ) -> List[Dict[str, Any]]:
        return [
            {
                "medication_name": "Amoxicillin",
                "prescribed_dosage": "500mg",
                "frequency": "Three times daily (TID)",
                "duration": "7 days",
                "instructions": "Take with water after meals. Complete full 7-day course.",
                "requires_confirmation": False,
                "warnings": []
            },
            {
                "medication_name": "Ibuprofen",
                "prescribed_dosage": "400mg",
                "frequency": "Every 8 hours as needed",
                "duration": "5 days",
                "instructions": "Take for mild to moderate pain.",
                "requires_confirmation": True,
                "warnings": ["Confirm frequency with pharmacist if taking with other NSAIDs."]
            }
        ]
