from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import uuid


class IMemoryRepository(ABC):
    @abstractmethod
    async def store_context(self, patient_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def retrieve_context(self, patient_id: str, query_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def get_relevant_history(self, patient_id: str, limit: int = 5) -> List[Dict[str, Any]]: pass


class InMemoryMemoryRepository(IMemoryRepository):
    def __init__(self):
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    async def store_context(self, patient_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        if patient_id not in self._store:
            self._store[patient_id] = []
        entry_id = f"mem_{uuid.uuid4().hex[:10]}"
        record = {
            "memory_id": entry_id,
            "patient_id": patient_id,
            "timestamp": "2026-08-14T23:51:00Z",
            **context_data
        }
        self._store[patient_id].append(record)
        return record

    async def retrieve_context(self, patient_id: str, query_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        history = self._store.get(patient_id, [])
        if not query_keywords:
            return history[-5:]
        filtered = []
        for record in history:
            text = str(record).lower()
            if any(kw.lower() in text for kw in query_keywords):
                filtered.append(record)
        return filtered if filtered else history[-3:]

    async def get_relevant_history(self, patient_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self._store.get(patient_id, [])[-limit:]


class IDoctorBridgeRepository(ABC):
    @abstractmethod
    async def save_brief(self, brief_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_brief(self, brief_id: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def save_questions(self, brief_id: str, questions: List[str]) -> Dict[str, Any]: pass
    @abstractmethod
    async def save_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_review(self, review_id: str) -> Optional[Dict[str, Any]]: pass


class InMemoryDoctorBridgeRepository(IDoctorBridgeRepository):
    def __init__(self):
        self._briefs: Dict[str, Dict[str, Any]] = {}
        self._questions: Dict[str, List[str]] = {}
        self._reviews: Dict[str, Dict[str, Any]] = {}

    async def save_brief(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        brief_id = brief_data.get("brief_id") or f"brief_{uuid.uuid4().hex[:10]}"
        brief_data["brief_id"] = brief_id
        self._briefs[brief_id] = brief_data
        return brief_data

    async def get_brief(self, brief_id: str) -> Optional[Dict[str, Any]]:
        return self._briefs.get(brief_id)

    async def save_questions(self, brief_id: str, questions: List[str]) -> Dict[str, Any]:
        self._questions[brief_id] = questions
        return {"brief_id": brief_id, "questions": questions}

    async def save_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        review_id = review_data.get("review_id") or f"rev_{uuid.uuid4().hex[:10]}"
        review_data["review_id"] = review_id
        review_data["is_clinician_feedback"] = True
        self._reviews[review_id] = review_data
        return review_data

    async def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        return self._reviews.get(review_id)


class ITimelineRepository(ABC):
    @abstractmethod
    async def get_events(self, patient_id: str) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def get_summary(self, patient_id: str) -> Dict[str, Any]: pass
    @abstractmethod
    async def add_event(self, patient_id: str, event: Dict[str, Any]) -> Dict[str, Any]: pass


class InMemoryTimelineRepository(ITimelineRepository):
    def __init__(self):
        self._events: Dict[str, List[Dict[str, Any]]] = {}

    async def get_events(self, patient_id: str) -> List[Dict[str, Any]]:
        return self._events.get(patient_id, [
            {
                "event_id": "evt_initial_01",
                "patient_id": patient_id,
                "timestamp": "2026-08-01T10:00:00Z",
                "event_type": "SYMPTOM_REPORTED",
                "description": "Patient reported acute right lower quadrant abdominal pain.",
                "source": "IntakeAgent"
            }
        ])

    async def get_summary(self, patient_id: str) -> Dict[str, Any]:
        events = await self.get_events(patient_id)
        return {
            "patient_id": patient_id,
            "total_events": len(events),
            "summary_narrative": f"Patient has {len(events)} recorded healthcare events. Recent onset of abdominal symptoms.",
            "last_event_timestamp": events[-1]["timestamp"] if events else None
        }

    async def add_event(self, patient_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        if patient_id not in self._events:
            self._events[patient_id] = []
        evt_id = event.get("event_id") or f"evt_{uuid.uuid4().hex[:10]}"
        event["event_id"] = evt_id
        event["patient_id"] = patient_id
        if "timestamp" not in event:
            event["timestamp"] = "2026-08-14T23:51:00Z"
        self._events[patient_id].append(event)
        return event


class IReferralRepository(ABC):
    @abstractmethod
    async def save_referral(self, referral_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_referral(self, referral_id: str) -> Optional[Dict[str, Any]]: pass


class InMemoryReferralRepository(IReferralRepository):
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    async def save_referral(self, referral_data: Dict[str, Any]) -> Dict[str, Any]:
        ref_id = referral_data.get("referral_id") or f"ref_{uuid.uuid4().hex[:10]}"
        referral_data["referral_id"] = ref_id
        referral_data["disclaimer"] = "Navigation guidance, not a diagnosis."
        self._store[ref_id] = referral_data
        return referral_data

    async def get_referral(self, referral_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(referral_id)


class ICarePlanRepository(ABC):
    @abstractmethod
    async def save_care_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_care_plan(self, care_plan_id: str) -> Optional[Dict[str, Any]]: pass


class InMemoryCarePlanRepository(ICarePlanRepository):
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    async def save_care_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        plan_id = plan_data.get("care_plan_id") or f"plan_{uuid.uuid4().hex[:10]}"
        plan_data["care_plan_id"] = plan_id
        self._store[plan_id] = plan_data
        return plan_data

    async def get_care_plan(self, care_plan_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(care_plan_id)


memory_repository = InMemoryMemoryRepository()
doctor_bridge_repository = InMemoryDoctorBridgeRepository()
timeline_repository = InMemoryTimelineRepository()
referral_repository = InMemoryReferralRepository()
care_plan_repository = InMemoryCarePlanRepository()
