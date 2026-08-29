from abc import ABC, abstractmethod
from typing import Any, Dict, List
from src.services.ai_contracts.base_ai import BaseAIService


class IRAGRetrieverService(BaseAIService):
    """
    Contract interface for vector store clinical guideline retrieval (ChromaDB).
    """

    @abstractmethod
    async def retrieve_evidence(
        self, query_symptoms: List[str], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves matching clinical evidence guidelines from ChromaDB based on query symptoms.
        """
        pass


class MockRAGRetrieverService(IRAGRetrieverService):
    """
    Mock implementation for local backend testing.
    """

    async def check_health(self) -> bool:
        return True

    async def retrieve_evidence(
        self, query_symptoms: List[str], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        return [
            {
                "document_id": "guideline_appendicitis_001",
                "title": "NICE Clinical Guidelines: Acute Abdominal Pain Triage",
                "content": "Right lower quadrant pain accompanied by fever and elevated WBC strongly indicates acute appendicitis. Requires immediate Surgical evaluation.",
                "relevance_score": 0.94,
                "specialty": "General Surgery",
                "urgency": "URGENT",
            },
            {
                "document_id": "guideline_gastro_004",
                "title": "ACG Guidelines on Acute Gastroenteritis",
                "content": "Diffuse abdominal pain with diarrhea and vomiting typically managed with oral rehydration.",
                "relevance_score": 0.72,
                "specialty": "Gastroenterology",
                "urgency": "ROUTINE",
            },
        ]
