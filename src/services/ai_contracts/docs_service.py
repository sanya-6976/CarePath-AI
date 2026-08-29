from abc import ABC, abstractmethod
from typing import Any, Dict, List
from src.services.ai_contracts.base_ai import BaseAIService


class IDocumentOCRService(BaseAIService):
    """
    Contract interface for AI Teammate responsible for Medical Document & Prescription OCR models.
    """

    @abstractmethod
    async def extract_medical_report(
        self, document_url_or_path: str
    ) -> Dict[str, Any]:
        """
        Extracts structured lab values, diagnostic reports, and prescription items from medical PDFs/images.
        """
        pass


class MockDocumentOCRService(IDocumentOCRService):
    """
    Mock implementation used for backend unit testing prior to AI model deployment.
    """

    async def check_health(self) -> bool:
        return True

    async def extract_medical_report(
        self, document_url_or_path: str
    ) -> Dict[str, Any]:
        return {
            "document_type": "Complete Blood Count (CBC) Lab Report",
            "extracted_values": {
                "WBC": {"value": 13.5, "unit": "10^3/uL", "flag": "HIGH"},
                "RBC": {"value": 4.5, "unit": "10^6/uL", "flag": "NORMAL"},
                "Hemoglobin": {"value": 14.1, "unit": "g/dL", "flag": "NORMAL"},
            },
            "raw_text_summary": "Patient displays mild leukocytosis consistent with acute infection/inflammation.",
        }
