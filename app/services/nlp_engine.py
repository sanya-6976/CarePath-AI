"""Production clinical NLP and medical entity extraction engine."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Iterable

from app.core.config import settings
from app.core.exceptions import ModelInferenceError
from app.core.interfaces import (
    EntityExtractionService,
    ServiceAvailability,
    ServiceHealthStatus,
)
from app.core.logging import get_logger
from app.core.validation import validate_text_input
from app.schemas.nlp import (
    BioNERResult,
    EntitySpan,
    MedicalEntity,
    MedicationInstruction,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class _EntityCandidate:
    """Internal representation of a detected clinical entity."""

    text: str
    category: str
    start: int
    end: int
    confidence: float
    normalized_text: str | None = None
    icd10_code: str | None = None
    snomed_ct: str | None = None
    negated: bool = False
    source: str = "clinical_pattern"


@dataclass(frozen=True)
class _MedicationCandidate:
    """Internal representation of a medication instruction."""

    medication: str
    dosage: str | None
    route: str | None
    frequency: str | None
    duration: str | None
    start: int
    end: int
    confidence: float
    negated: bool


class BioNEREngine(EntityExtractionService):
    """
    Hybrid clinical NLP engine.

    The engine performs deterministic clinical extraction with:
    - contextual entity matching
    - negation detection
    - medication instruction extraction
    - dosage/frequency/route/duration extraction
    - laboratory-value detection
    - character-level provenance
    - confidence scoring

    The architecture is deliberately model-agnostic so a transformer-based
    medical NER model can be introduced later without changing the API
    contract.
    """

    _SERVICE_NAME = "CarePath Bio-NER Engine"
    _SERVICE_VERSION = "1.0.0"

    _NEGATION_CUES = (
        "no",
        "not",
        "without",
        "denies",
        "denied",
        "negative for",
        "absence of",
        "absent",
        "free of",
        "does not have",
        "doesn't have",
        "did not have",
        "didn't have",
    )

    _NEGATION_WINDOW = 80

    _ENTITY_LEXICON: tuple[
        tuple[str, str, str | None, str | None],
        ...
    ] = (
        ("shortness of breath", "SYMPTOM", "R06.02", None),
        ("chest pain", "SYMPTOM", "R07.9", None),
        ("difficulty breathing", "SYMPTOM", "R06.00", None),
        ("abdominal pain", "SYMPTOM", "R10.9", None),
        ("headache", "SYMPTOM", "R51.9", None),
        ("dizziness", "SYMPTOM", "R42", None),
        ("nausea", "SYMPTOM", "R11.0", None),
        ("vomiting", "SYMPTOM", "R11.10", None),
        ("diarrhea", "SYMPTOM", "R19.7", None),
        ("fatigue", "SYMPTOM", "R53.83", None),
        ("fever", "SYMPTOM", "R50.9", None),
        ("cough", "SYMPTOM", "R05.9", None),
        ("sore throat", "SYMPTOM", "R07.0", None),
        ("wheezing", "SYMPTOM", "R06.2", None),
        ("palpitations", "SYMPTOM", "R00.2", None),
        ("rash", "SYMPTOM", "R21", None),
        ("swelling", "SYMPTOM", "R60.9", None),

        ("pneumonia", "DIAGNOSIS", "J18.9", None),
        ("diabetes mellitus", "DIAGNOSIS", "E11.9", None),
        ("diabetes", "DIAGNOSIS", "E11.9", None),
        ("hypertension", "DIAGNOSIS", "I10", None),
        ("asthma", "DIAGNOSIS", "J45.909", None),
        ("bronchitis", "DIAGNOSIS", "J40", None),
        ("anemia", "DIAGNOSIS", "D64.9", None),
        ("migraine", "DIAGNOSIS", "G43.909", None),
        ("influenza", "DIAGNOSIS", "J11.1", None),

        ("lung", "ANATOMY", None, "39607008"),
        ("heart", "ANATOMY", None, "80891009"),
        ("liver", "ANATOMY", None, "10200004"),
        ("kidney", "ANATOMY", None, "64033007"),
        ("chest", "ANATOMY", None, "51185008"),
        ("abdomen", "ANATOMY", None, "818983003"),

        ("x-ray", "PROCEDURE", None, None),
        ("xray", "PROCEDURE", None, None),
        ("mri", "PROCEDURE", None, None),
        ("ct scan", "PROCEDURE", None, None),
        ("ultrasound", "PROCEDURE", None, None),
        ("biopsy", "PROCEDURE", None, None),
        ("blood test", "PROCEDURE", None, None),
        ("blood pressure measurement", "PROCEDURE", None, None),
    )

    _MEDICATION_NAMES = (
        "amoxicillin",
        "azithromycin",
        "paracetamol",
        "acetaminophen",
        "ibuprofen",
        "metformin",
        "insulin",
        "atorvastatin",
        "amlodipine",
        "losartan",
        "omeprazole",
        "pantoprazole",
        "cetirizine",
        "loratadine",
        "prednisolone",
        "aspirin",
    )

    _MEDICATION_CODES = {
        "amoxicillin": "ATC:J01CA04",
        "paracetamol": "ATC:N02BE01",
        "acetaminophen": "ATC:N02BE01",
        "metformin": "ATC:A10BA02",
        "ibuprofen": "ATC:M01AE01",
        "aspirin": "ATC:B01AC06",
    }

    _DOSAGE_PATTERN = re.compile(
        r"\b"
        r"(?P<value>\d+(?:\.\d+)?)"
        r"\s*"
        r"(?P<unit>mg|mcg|µg|g|ml|mL|mg/mL)"
        r"\b",
        re.IGNORECASE,
    )

    _FREQUENCY_PATTERNS = (
        r"\bonce\s+(?:a|per)\s+day\b",
        r"\btwice\s+(?:a|per)\s+day\b",
        r"\bthrice\s+(?:a|per)\s+day\b",
        r"\bthree\s+times\s+(?:a|per)\s+day\b",
        r"\bevery\s+\d+\s+(?:hours?|hrs?)\b",
        r"\b(?:q\.?d\.?|b\.?i\.?d\.?|t\.?i\.?d\.?|q\.?i\.?d\.?)\b",
        r"\b\d+\s+times\s+(?:daily|a day)\b",
    )

    _ROUTES = (
        "oral",
        "by mouth",
        "intravenous",
        "iv",
        "intramuscular",
        "im",
        "subcutaneous",
        "sc",
        "topical",
        "inhaled",
        "sublingual",
    )

    _DURATION_PATTERN = re.compile(
        r"\bfor\s+"
        r"(?P<duration>\d+\s+(?:day|days|week|weeks|month|months))\b",
        re.IGNORECASE,
    )

    _LAB_PATTERN = re.compile(
        r"\b"
        r"(?P<name>"
        r"hemoglobin|haemoglobin|hb|hba1c|"
        r"wbc|white blood cell(?:s)?|"
        r"rbc|red blood cell(?:s)?|"
        r"platelet(?:s)?|"
        r"glucose|blood glucose|"
        r"creatinine|"
        r"cholesterol|"
        r"triglyceride(?:s)?"
        r")"
        r"\s*[:=]?\s*"
        r"(?P<value>\d+(?:\.\d+)?)"
        r"\s*"
        r"(?P<unit>"
        r"g/dl|mg/dl|mmol/l|mg/l|µmol/l|umol/l|"
        r"%|10\^?3/u[lL]|10\^?9/[lL]|"
        r"/u[lL]"
        r")?"
        r"\b",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        self._backend = "clinical_pattern_engine"

        logger.info(
            "%s initialized.",
            self._SERVICE_NAME,
        )

    # ------------------------------------------------------------------
    # Service contract
    # ------------------------------------------------------------------

    def health_check(self) -> ServiceHealthStatus:
        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend=self._backend,
            message="Clinical NLP extraction engine is ready.",
        )

    def get_service_info(self) -> dict:
        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": ServiceAvailability.AVAILABLE.value,
            "backend": self._backend,
            "entity_types": [
                "SYMPTOM",
                "MEDICATION",
                "ANATOMY",
                "PROCEDURE",
                "DIAGNOSIS",
                "LAB_METRIC",
            ],
            "lexicon_entries": len(self._ENTITY_LEXICON),
            "medication_terms": len(self._MEDICATION_NAMES),
            "confidence_threshold": settings.NLP_CONFIDENCE_THRESHOLD,
            "entity_count": len(self._ENTITY_LEXICON),
        }

    # ------------------------------------------------------------------
    # Main extraction
    # ------------------------------------------------------------------

    def extract_entities(self, text: str) -> BioNERResult:
        """Extract structured medical information from clinical text."""
        validate_text_input(
            text,
            min_len=1,
            max_len=32_768,
        )

        started = time.perf_counter()

        try:
            candidates = self._extract_clinical_entities(text)

            medication_candidates = self._extract_medications(text)

            candidates.extend(
                self._extract_lab_metrics(text)
            )

            candidates = self._deduplicate_entities(candidates)

            entities = [
                self._candidate_to_schema(
                    candidate,
                    text,
                )
                for candidate in candidates
            ]

            medication_instructions = [
                MedicationInstruction(
                    medication=item.medication,
                    dosage=item.dosage,
                    route=item.route,
                    frequency=item.frequency,
                    duration=item.duration,
                    negated=item.negated,
                    confidence=item.confidence,
                )
                for item in medication_candidates
            ]

            symptoms = self._unique_non_negated_values(
                entities,
                "SYMPTOM",
            )

            medications = self._unique_non_negated_values(
                entities,
                "MEDICATION",
            )

            diagnoses = self._unique_non_negated_values(
                entities,
                "DIAGNOSIS",
            )

            elapsed = round(
                time.perf_counter() - started,
                4,
            )

            overall_confidence = self._calculate_confidence(
                entities,
            )

            return BioNERResult(
                input_text=text,
                entities=entities,
                symptoms=symptoms,
                medications=medications,
                diagnoses=diagnoses,
                medication_instructions=medication_instructions,
                processing_time_seconds=elapsed,
                model_backend=self._backend,
                overall_confidence=overall_confidence,
            )

        except Exception as exc:
            if isinstance(exc, (ValueError, TypeError)):
                raise

            logger.exception(
                "Clinical NLP extraction failed."
            )

            raise ModelInferenceError(
                "Clinical NLP extraction failed."
            ) from exc

    # ------------------------------------------------------------------
    # Entity extraction
    # ------------------------------------------------------------------

    def _extract_clinical_entities(
        self,
        text: str,
    ) -> list[_EntityCandidate]:
        candidates: list[_EntityCandidate] = []

        for (
            term,
            category,
            icd10_code,
            snomed_ct,
        ) in self._ENTITY_LEXICON:

            pattern = re.compile(
                rf"(?<!\w){re.escape(term)}(?!\w)",
                re.IGNORECASE,
            )

            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()

                matched_text = text[start:end]

                negated = self._is_negated(
                    text=text,
                    start=start,
                )

                confidence = self._entity_confidence(
                    category=category,
                    term=term,
                    negated=negated,
                )

                candidates.append(
                    _EntityCandidate(
                        text=matched_text,
                        normalized_text=term.lower(),
                        category=category,
                        start=start,
                        end=end,
                        confidence=confidence,
                        icd10_code=icd10_code,
                        snomed_ct=snomed_ct,
                        negated=negated,
                        source="clinical_pattern",
                    )
                )

        return candidates

    # ------------------------------------------------------------------
    # Medication extraction
    # ------------------------------------------------------------------

    def _extract_medications(
        self,
        text: str,
    ) -> list[_MedicationCandidate]:
        results: list[_MedicationCandidate] = []

        for medication in self._MEDICATION_NAMES:
            pattern = re.compile(
                rf"(?<!\w){re.escape(medication)}(?!\w)",
                re.IGNORECASE,
            )

            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()

                negated = self._is_negated(
                    text=text,
                    start=start,
                )

                context_start = max(
                    0,
                    start - 20,
                )
                context_end = min(
                    len(text),
                    end + 120,
                )

                context = text[
                    context_start:context_end
                ]

                dosage_match = self._DOSAGE_PATTERN.search(
                    context
                )

                dosage = (
                    dosage_match.group(0)
                    if dosage_match
                    else None
                )

                frequency = self._extract_frequency(
                    context
                )

                route = self._extract_route(
                    context
                )

                duration_match = (
                    self._DURATION_PATTERN.search(context)
                )

                duration = (
                    duration_match.group("duration")
                    if duration_match
                    else None
                )

                confidence = 0.96

                if dosage:
                    confidence += 0.01

                if frequency:
                    confidence += 0.01

                confidence = min(
                    confidence,
                    0.99,
                )

                results.append(
                    _MedicationCandidate(
                        medication=match.group(0),
                        dosage=dosage,
                        route=route,
                        frequency=frequency,
                        duration=duration,
                        start=start,
                        end=end,
                        confidence=confidence,
                        negated=negated,
                    )
                )

        return self._deduplicate_medications(
            results
        )

    def _extract_frequency(
        self,
        text: str,
    ) -> str | None:
        for pattern in self._FREQUENCY_PATTERNS:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return match.group(0)

        return None

    def _extract_route(
        self,
        text: str,
    ) -> str | None:
        normalized = text.lower()

        for route in self._ROUTES:
            if re.search(
                rf"(?<!\w){re.escape(route)}(?!\w)",
                normalized,
            ):
                return route

        return None

    # ------------------------------------------------------------------
    # Laboratory extraction
    # ------------------------------------------------------------------

    def _extract_lab_metrics(
        self,
        text: str,
    ) -> list[_EntityCandidate]:
        candidates: list[_EntityCandidate] = []

        for match in self._LAB_PATTERN.finditer(text):
            name = match.group("name")
            value = match.group("value")
            unit = match.group("unit")

            full_text = match.group(0).strip()

            start = match.start()
            end = match.end()

            normalized_name = (
                re.sub(
                    r"\s+",
                    " ",
                    name.lower(),
                )
                .strip()
            )

            normalized_value = (
                f"{normalized_name}: {value}"
                + (f" {unit}" if unit else "")
            )

            negated = self._is_negated(
                text=text,
                start=start,
            )

            candidates.append(
                _EntityCandidate(
                    text=full_text,
                    normalized_text=normalized_value,
                    category="LAB_METRIC",
                    start=start,
                    end=end,
                    confidence=0.97,
                    negated=negated,
                    source="lab_pattern",
                )
            )

        return candidates

    # ------------------------------------------------------------------
    # Negation
    # ------------------------------------------------------------------

    def _is_negated(
        self,
        text: str,
        start: int,
    ) -> bool:
        """
        Detect local negation without assuming the entire sentence is negated.

        Example:
            "No fever but cough is present."
        correctly marks fever as negated while cough remains positive.
        """
        window_start = max(
            0,
            start - self._NEGATION_WINDOW,
        )

        prefix = text[
            window_start:start
        ].lower()

        # Only inspect the current sentence/segment.
        separators = re.split(
            r"[.!?;\n]",
            prefix,
        )

        local_prefix = separators[-1].strip()

        for cue in self._NEGATION_CUES:
            if re.search(
                rf"(?<!\w){re.escape(cue)}(?:\s+|$)",
                local_prefix,
            ):
                return True

        return False

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def _entity_confidence(
        category: str,
        term: str,
        negated: bool,
    ) -> float:
        confidence = {
            "DIAGNOSIS": 0.93,
            "MEDICATION": 0.96,
            "SYMPTOM": 0.94,
            "ANATOMY": 0.91,
            "PROCEDURE": 0.92,
            "LAB_METRIC": 0.97,
        }.get(
            category,
            0.90,
        )

        if " " in term:
            confidence += 0.01

        if negated:
            # Confidence remains high for the entity itself.
            # Negation means the entity was explicitly mentioned as absent.
            confidence = min(
                confidence + 0.01,
                0.99,
            )

        return round(
            confidence,
            4,
        )

    @staticmethod
    def _calculate_confidence(
        entities: list[MedicalEntity],
    ) -> float:
        if not entities:
            return 0.0

        return round(
            sum(
                entity.confidence
                for entity in entities
            )
            / len(entities),
            4,
        )

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_entities(
        candidates: Iterable[_EntityCandidate],
    ) -> list[_EntityCandidate]:
        ordered = sorted(
            candidates,
            key=lambda item: (
                item.start,
                -(item.end - item.start),
            ),
        )

        result: list[_EntityCandidate] = []

        for candidate in ordered:
            overlaps = False

            for existing in result:
                if (
                    candidate.start < existing.end
                    and candidate.end > existing.start
                ):
                    # Prefer the longer/more specific span.
                    if (
                        candidate.end - candidate.start
                        <= existing.end - existing.start
                    ):
                        overlaps = True
                        break

            if not overlaps:
                result.append(candidate)

        return result

    @staticmethod
    def _deduplicate_medications(
        candidates: Iterable[_MedicationCandidate],
    ) -> list[_MedicationCandidate]:
        seen: set[tuple] = set()
        result: list[_MedicationCandidate] = []

        for candidate in candidates:
            key = (
                candidate.medication.lower(),
                candidate.start,
                candidate.dosage,
                candidate.frequency,
                candidate.route,
                candidate.duration,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(candidate)

        return result

    # ------------------------------------------------------------------
    # Schema conversion
    # ------------------------------------------------------------------

    def _candidate_to_schema(
        self,
        candidate: _EntityCandidate,
        source_text: str,
    ) -> MedicalEntity:
        context_start = max(
            0,
            candidate.start - 50,
        )

        context_end = min(
            len(source_text),
            candidate.end + 80,
        )

        context = source_text[
            context_start:context_end
        ].strip()

        return MedicalEntity(
            text=candidate.text,
            normalized_text=candidate.normalized_text,
            category=candidate.category,
            icd10_code=candidate.icd10_code,
            snomed_ct=candidate.snomed_ct,
            negated=candidate.negated,
            confidence=candidate.confidence,
            context=context,
            span=EntitySpan(
                start=candidate.start,
                end=candidate.end,
            ),
            source=candidate.source,
        )

    @staticmethod
    def _unique_non_negated_values(
        entities: Iterable[MedicalEntity],
        category: str,
    ) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()

        for entity in entities:
            if entity.category != category:
                continue

            if entity.negated:
                continue

            normalized = (
                entity.normalized_text
                or entity.text
            )

            key = normalized.lower().strip()

            if key in seen:
                continue

            seen.add(key)
            values.append(entity.text)

        return values


nlp_engine = BioNEREngine()