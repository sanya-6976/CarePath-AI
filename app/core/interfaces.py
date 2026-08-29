"""Abstract service interfaces for CarePath AI modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.schemas.diagnosis import PatientCarePathSynthesis
    from app.schemas.nlp import BioNERResult
    from app.schemas.ocr import OCRResult
    from app.schemas.rag import RAGQueryResponse
    from app.schemas.vision import VisionAnalysisResult


class ServiceAvailability(str, Enum):
    """Coarse-grained availability classification for AI services."""

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ServiceHealthStatus:
    """Immutable service readiness snapshot."""

    availability: ServiceAvailability
    message: Optional[str] = None
    backend: Optional[str] = None

    @property
    def is_ok(self) -> bool:
        """Return True only when the service is fully operational."""
        return self.availability == ServiceAvailability.AVAILABLE

    def as_dict(self) -> dict[str, Optional[str]]:
        """Return a JSON-serializable representation."""
        return {
            "availability": self.availability.value,
            "message": self.message,
            "backend": self.backend,
        }


class BaseAIService(ABC):
    """Base contract shared by all CarePath AI services."""

    @abstractmethod
    def health_check(self) -> ServiceHealthStatus:
        """Return the current service readiness state."""
        ...

    @abstractmethod
    def get_service_info(self) -> dict:
        """Return non-sensitive service metadata."""
        ...


class TextExtractionService(BaseAIService):
    """Contract for OCR and medical document text extraction."""

    @abstractmethod
    def extract_text(
        self,
        image_bytes: bytes,
        filename: str = "document.png",
        content_type: Optional[str] = None,
    ) -> "OCRResult":
        """
        Extract structured text from an image or PDF.

        Implementations must not fabricate content when extraction fails.
        """
        ...


class VisionAnalysisService(BaseAIService):
    """Contract for medical computer-vision analysis."""

    @abstractmethod
    def analyze_image(
        self,
        image_bytes: bytes,
        filename: str = "image.dcm",
    ) -> "VisionAnalysisResult":
        """Run computer-vision analysis on image/DICOM bytes."""
        ...


class EntityExtractionService(BaseAIService):
    """Contract for clinical NLP and medical entity extraction."""

    @abstractmethod
    def extract_entities(
        self,
        text: str,
    ) -> "BioNERResult":
        """Extract structured medical entities from clinical text."""
        ...


class KnowledgeRetrievalService(BaseAIService):
    """Contract for medical knowledge retrieval/RAG."""

    @abstractmethod
    def query_guidelines(
        self,
        query: str,
        top_k: int = 3,
    ) -> "RAGQueryResponse":
        """Retrieve relevant medical evidence."""
        ...


class ClinicalSynthesisService(BaseAIService):
    """Contract for multimodal clinical synthesis."""

    @abstractmethod
    def synthesize_patient_case(
        self,
        clinical_notes: Optional[str] = None,
        document_bytes: Optional[bytes] = None,
        document_filename: str = "doc.png",
        image_bytes: Optional[bytes] = None,
        image_filename: str = "xray.png",
    ) -> "PatientCarePathSynthesis":
        """Synthesize multimodal patient information."""
        ...


class PatientSummaryService(BaseAIService):
    """Contract for structured patient summary generation."""

    @abstractmethod
    def generate_summary(
        self,
        request: "PatientSummaryRequest",
    ) -> "PatientSummaryReport":
        """Generate a validated structured patient summary."""
        ...


class CaseQuestionService(BaseAIService):
    """Contract for case-specific doctor question generation."""

    @abstractmethod
    def generate_questions(
        self,
        request: "CaseQuestionRequest",
    ) -> "CaseQuestionsReport":
        """Generate validated, case-specific questions for a clinician."""
        ...


class ClinicalExtractionService(BaseAIService):
    """Contract for structured clinical information extraction."""

    @abstractmethod
    def extract_clinical_info(
        self,
        request: "ClinicalExtractionRequest",
    ) -> "ClinicalExtractionReport":
        """Extract structured medical entities, facts, and relationships from multi-modal clinical inputs."""
        ...


class DoctorFeedbackService(BaseAIService):
    """Contract for doctor feedback interpretation and memory candidate structuring."""

    @abstractmethod
    def interpret_feedback(
        self,
        request: "DoctorFeedbackRequest",
    ) -> "DoctorFeedbackInterpretationReport":
        """Interpret structured or unstructured clinician feedback into memory-ready clinical objects."""
        ...


class TreatmentResponseService(BaseAIService):
    """Contract for comparing treatment events against clinical outcomes."""

    @abstractmethod
    def analyze_treatment_response(
        self,
        request: "TreatmentResponseRequest",
    ) -> "TreatmentResponseReport":
        """Analyze documented treatment events and evaluate clinical outcome response."""
        ...


class FollowUpIntelligenceService(BaseAIService):
    """Contract for identifying care-continuity follow-up requirements."""

    @abstractmethod
    def analyze_follow_up(
        self,
        request: "FollowUpIntelligenceRequest",
    ) -> "FollowUpIntelligenceReport":
        """Analyze documented history, trends, and instructions to identify follow-up needs."""
        ...


class PersonalizedCarePlanService(BaseAIService):
    """Contract for generating structured continuity-of-care plans."""

    @abstractmethod
    def generate_care_plan(
        self,
        request: "PersonalizedCarePlanRequest",
    ) -> "PersonalizedCarePlanReport":
        """Generate structured continuity care plan grounding doctor orders and patient context."""
        ...





