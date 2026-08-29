from typing import Optional, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import Visit, SymptomSession, PatientSymptom, Medication, MedicalFile
from database.crud.utils import create_record, get_record, update_record, delete_record

def create_visit(session: Session, **kwargs) -> Visit:
    """Creates a new visit record."""
    return create_record(session, Visit, **kwargs)

def get_visit(session: Session, visit_id: Any) -> Optional[Visit]:
    """Retrieves a visit by visit_id."""
    return get_record(session, Visit, visit_id)

def create_session(session: Session, **kwargs) -> SymptomSession:
    """Creates a new symptom session."""
    return create_record(session, SymptomSession, **kwargs)

def create_symptom(session: Session, **kwargs) -> PatientSymptom:
    """Creates a patient symptom record."""
    return create_record(session, PatientSymptom, **kwargs)

def create_medication(session: Session, **kwargs) -> Medication:
    """Creates a medication record."""
    return create_record(session, Medication, **kwargs)

def get_user_medications(session: Session, user_id: Any, status: Optional[str] = None) -> List[Medication]:
    """Retrieves medications for a user, optionally filtered by status."""
    stmt = select(Medication).where(Medication.user_id == user_id)
    if status:
        stmt = stmt.where(Medication.status == status)
    return list(session.scalars(stmt).all())

def get_medication_by_id(session: Session, medication_id: Any) -> Optional[Medication]:
    """Retrieves a medication record by medication_id."""
    return get_record(session, Medication, medication_id)

def update_medication_status(session: Session, medication_id: Any, status: str) -> Optional[Medication]:
    """Updates status of a medication record."""
    return update_record(session, Medication, medication_id, status=status)

def create_medical_file(session: Session, **kwargs) -> MedicalFile:
    """Creates a metadata record for an uploaded medical file."""
    return create_record(session, MedicalFile, **kwargs)

def get_user_medical_files(session: Session, user_id: Any, file_type: Optional[str] = None) -> List[MedicalFile]:
    """Retrieves medical files uploaded by a user, optionally filtered by file_type."""
    stmt = select(MedicalFile).where(MedicalFile.user_id == user_id)
    if file_type:
        stmt = stmt.where(MedicalFile.file_type == file_type)
    return list(session.scalars(stmt).all())

def get_medical_file_by_id(session: Session, file_id: Any) -> Optional[MedicalFile]:
    """Retrieves a medical file record by file_id."""
    return get_record(session, MedicalFile, file_id)

def update_analysis_status(session: Session, file_id: Any, status: str) -> Optional[MedicalFile]:
    """Updates the analysis status of a specific medical file."""
    return update_record(session, MedicalFile, file_id, analysis_status=status)

def delete_medical_file(session: Session, file_id: Any) -> bool:
    """Deletes a medical file record by file_id."""
    return delete_record(session, MedicalFile, file_id)

