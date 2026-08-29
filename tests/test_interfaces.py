"""Tests for Abstract Service Interfaces (app/core/interfaces.py).

Validates:
- ABC enforcement (cannot instantiate abstract classes directly).
- Each concrete engine implements the correct interface (isinstance checks).
- health_check() returns a ServiceHealthStatus with valid availability.
- get_service_info() returns a dict with required keys.
- ServiceHealthStatus.is_ok property behaves correctly.
"""
import pytest

from app.core.interfaces import (
    BaseAIService,
    TextExtractionService,
    VisionAnalysisService,
    EntityExtractionService,
    KnowledgeRetrievalService,
    ClinicalSynthesisService,
    ServiceHealthStatus,
    ServiceAvailability,
)
from app.services.ocr_engine import ocr_engine, OCREngine
from app.services.vision_engine import vision_engine, VisionEngine
from app.services.nlp_engine import nlp_engine, BioNEREngine
from app.services.rag_engine import rag_engine, RAGKnowledgeEngine
from app.services.carepath_engine import carepath_engine, CarePathEngine


# ---------------------------------------------------------------------------
# ServiceHealthStatus
# ---------------------------------------------------------------------------

class TestServiceHealthStatus:

    def test_available_is_ok(self):
        status = ServiceHealthStatus(availability=ServiceAvailability.AVAILABLE)
        assert status.is_ok is True

    def test_degraded_not_ok(self):
        status = ServiceHealthStatus(availability=ServiceAvailability.DEGRADED)
        assert status.is_ok is False

    def test_unavailable_not_ok(self):
        status = ServiceHealthStatus(availability=ServiceAvailability.UNAVAILABLE)
        assert status.is_ok is False

    def test_as_dict_keys(self):
        status = ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            message="All good.",
            backend="chromadb",
        )
        d = status.as_dict()
        assert "availability" in d
        assert "message" in d
        assert "backend" in d
        assert d["availability"] == "available"

    def test_immutability(self):
        status = ServiceHealthStatus(availability=ServiceAvailability.AVAILABLE)
        with pytest.raises(Exception):
            status.availability = ServiceAvailability.DEGRADED  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ABC Enforcement
# ---------------------------------------------------------------------------

class TestABCEnforcement:
    """Concrete base classes cannot be instantiated directly."""

    def test_base_ai_service_is_abstract(self):
        with pytest.raises(TypeError):
            BaseAIService()  # type: ignore[abstract]

    def test_text_extraction_service_is_abstract(self):
        with pytest.raises(TypeError):
            TextExtractionService()  # type: ignore[abstract]

    def test_vision_analysis_service_is_abstract(self):
        with pytest.raises(TypeError):
            VisionAnalysisService()  # type: ignore[abstract]

    def test_entity_extraction_service_is_abstract(self):
        with pytest.raises(TypeError):
            EntityExtractionService()  # type: ignore[abstract]

    def test_knowledge_retrieval_service_is_abstract(self):
        with pytest.raises(TypeError):
            KnowledgeRetrievalService()  # type: ignore[abstract]

    def test_clinical_synthesis_service_is_abstract(self):
        with pytest.raises(TypeError):
            ClinicalSynthesisService()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Concrete Engine isinstance Checks
# ---------------------------------------------------------------------------

class TestEngineInterfaces:

    def test_ocr_engine_implements_text_extraction(self):
        assert isinstance(ocr_engine, TextExtractionService)
        assert isinstance(ocr_engine, BaseAIService)

    def test_vision_engine_implements_vision_analysis(self):
        assert isinstance(vision_engine, VisionAnalysisService)
        assert isinstance(vision_engine, BaseAIService)

    def test_nlp_engine_implements_entity_extraction(self):
        assert isinstance(nlp_engine, EntityExtractionService)
        assert isinstance(nlp_engine, BaseAIService)

    def test_rag_engine_implements_knowledge_retrieval(self):
        assert isinstance(rag_engine, KnowledgeRetrievalService)
        assert isinstance(rag_engine, BaseAIService)

    def test_carepath_engine_implements_clinical_synthesis(self):
        assert isinstance(carepath_engine, ClinicalSynthesisService)
        assert isinstance(carepath_engine, BaseAIService)


# ---------------------------------------------------------------------------
# health_check() — returns ServiceHealthStatus for all engines
# ---------------------------------------------------------------------------

REQUIRED_INFO_KEYS = {"name", "version", "status"}


class TestHealthCheck:

    def test_ocr_health_check_returns_status(self):
        status = ocr_engine.health_check()
        assert isinstance(status, ServiceHealthStatus)
        assert isinstance(status.availability, ServiceAvailability)

    def test_vision_health_check_returns_status(self):
        status = vision_engine.health_check()
        assert isinstance(status, ServiceHealthStatus)
        assert isinstance(status.availability, ServiceAvailability)

    def test_nlp_health_check_returns_status(self):
        status = nlp_engine.health_check()
        assert isinstance(status, ServiceHealthStatus)
        # NLP is pure Python — always available
        assert status.availability == ServiceAvailability.AVAILABLE

    def test_rag_health_check_returns_status(self):
        status = rag_engine.health_check()
        assert isinstance(status, ServiceHealthStatus)
        assert status.availability in list(ServiceAvailability)

    def test_carepath_health_check_returns_status(self):
        status = carepath_engine.health_check()
        assert isinstance(status, ServiceHealthStatus)
        # Aggregate status reflects sub-engines
        assert status.availability in list(ServiceAvailability)


# ---------------------------------------------------------------------------
# get_service_info() — returns dict with required keys
# ---------------------------------------------------------------------------

class TestGetServiceInfo:

    def _assert_required_keys(self, info: dict) -> None:
        for key in REQUIRED_INFO_KEYS:
            assert key in info, f"Missing required key '{key}' in service_info: {info}"
        # status must be a valid ServiceAvailability value
        valid_values = {a.value for a in ServiceAvailability}
        assert info["status"] in valid_values

    def test_ocr_service_info(self):
        info = ocr_engine.get_service_info()
        self._assert_required_keys(info)
        assert info["name"] == "CarePath OCR Engine"

    def test_vision_service_info(self):
        info = vision_engine.get_service_info()
        self._assert_required_keys(info)
        assert info["name"] == "CarePath Vision Engine"

    def test_nlp_service_info(self):
        info = nlp_engine.get_service_info()
        self._assert_required_keys(info)
        assert info["name"] == "CarePath Bio-NER Engine"
        assert "entity_count" in info

    def test_rag_service_info(self):
        info = rag_engine.get_service_info()
        self._assert_required_keys(info)
        assert info["name"] == "CarePath RAG Knowledge Engine"

    def test_carepath_service_info(self):
        info = carepath_engine.get_service_info()
        self._assert_required_keys(info)
        assert "sub_engines" in info
        sub = info["sub_engines"]
        assert set(sub.keys()) == {"ocr", "vision", "nlp", "rag"}
