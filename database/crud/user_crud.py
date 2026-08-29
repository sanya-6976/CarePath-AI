from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import User, PatientProfile, FamilyMember
from database.crud.utils import create_record, get_record, update_record, delete_record

def create_user(session: Session, **kwargs) -> User:
    """Creates a new user record."""
    return create_record(session, User, **kwargs)

def get_user(session: Session, user_id: Any) -> Optional[User]:
    """Retrieves a user by their user_id."""
    return get_record(session, User, user_id)

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Retrieves a user by their email address."""
    try:
        stmt = select(User).where(User.email == email)
        return session.scalars(stmt).first()
    except Exception as e:
        session.rollback()
        raise e

def update_user(session: Session, user_id: Any, **kwargs) -> Optional[User]:
    """Updates an existing user record."""
    return update_record(session, User, user_id, **kwargs)

def delete_user(session: Session, user_id: Any) -> bool:
    """Deletes a user record."""
    return delete_record(session, User, user_id)

def create_patient_profile(session: Session, **kwargs) -> PatientProfile:
    """Creates a patient profile linked to a user."""
    return create_record(session, PatientProfile, **kwargs)

def get_patient_profile(session: Session, user_id: Any) -> Optional[PatientProfile]:
    """Retrieves a patient profile by the associated user_id."""
    return get_record(session, PatientProfile, user_id)

def create_family_member(session: Session, **kwargs) -> FamilyMember:
    """Creates a family member association."""
    return create_record(session, FamilyMember, **kwargs)
