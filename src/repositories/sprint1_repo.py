from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import uuid


class IDocumentRepository(ABC):
    @abstractmethod
    async def save_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def update_status(self, document_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]: pass


class InMemoryDocumentRepository(IDocumentRepository):
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    async def save_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        doc_id = doc_data.get("document_id") or f"doc_{uuid.uuid4().hex[:10]}"
        doc_data["document_id"] = doc_id
        if "status" not in doc_data:
            doc_data["status"] = "uploaded"
        self._store[doc_id] = doc_data
        return doc_data

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(document_id)

    async def update_status(self, document_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if document_id in self._store:
            self._store[document_id]["status"] = status
            if result:
                self._store[document_id]["extracted_information"] = result.get("extracted_information", {})
                self._store[document_id]["warnings"] = result.get("warnings", [])
                self._store[document_id]["confidence"] = result.get("confidence")
                self._store[document_id]["document_type"] = result.get("document_type", self._store[document_id].get("document_type", "medical_report"))
            return self._store[document_id]
        return None


class IMedicationRepository(ABC):
    @abstractmethod
    async def save_medication(self, med_data: Dict[str, Any]) -> Dict[str, Any]: pass
    @abstractmethod
    async def get_medication(self, medication_id: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def list_medications(self, patient_id: Optional[str] = None) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def confirm_medication(self, medication_id: str) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def set_schedule(self, medication_id: str, schedule: Dict[str, Any]) -> Optional[Dict[str, Any]]: pass
    @abstractmethod
    async def log_action(self, medication_id: str, action: str, reason: Optional[str] = None) -> Optional[Dict[str, Any]]: pass


class InMemoryMedicationRepository(IMedicationRepository):
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    async def save_medication(self, med_data: Dict[str, Any]) -> Dict[str, Any]:
        med_id = med_data.get("medication_id") or f"med_{uuid.uuid4().hex[:10]}"
        med_data["medication_id"] = med_id
        if "confirmed" not in med_data:
            med_data["confirmed"] = False
        if "action_history" not in med_data:
            med_data["action_history"] = []
        self._store[med_id] = med_data
        return med_data

    async def get_medication(self, medication_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(medication_id)

    async def list_medications(self, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not patient_id:
            return list(self._store.values())
        return [m for m in self._store.values() if m.get("patient_id") == patient_id]

    async def confirm_medication(self, medication_id: str) -> Optional[Dict[str, Any]]:
        if medication_id in self._store:
            self._store[medication_id]["confirmed"] = True
            self._store[medication_id]["requires_confirmation"] = False
            return self._store[medication_id]
        return None

    async def set_schedule(self, medication_id: str, schedule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if medication_id in self._store:
            self._store[medication_id]["schedule"] = schedule
            return self._store[medication_id]
        return None

    async def log_action(self, medication_id: str, action: str, reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if medication_id in self._store:
            entry = {"action": action, "timestamp": "2026-08-14T23:51:00Z", "reason": reason}
            self._store[medication_id]["action_history"].append(entry)
            self._store[medication_id]["last_action"] = entry
            return self._store[medication_id]
        return None


# Singletons for memory repositories
document_repository = InMemoryDocumentRepository()
medication_repository = InMemoryMedicationRepository()
