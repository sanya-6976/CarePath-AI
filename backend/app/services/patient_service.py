from typing import Any, Optional, List
from sqlalchemy.orm import Session
from database.crud import user_crud
from database.models import PatientProfile
import uuid
from datetime import datetime, timezone, date

from database.crud.utils import safe_uuid

def calculate_dob(data: dict) -> date:
    dob_val = data.get("date_of_birth") or data.get("dob")
    if dob_val:
        if isinstance(dob_val, date):
            return dob_val
        if isinstance(dob_val, str):
            try:
                return datetime.strptime(dob_val, "%Y-%m-%d").date()
            except ValueError:
                pass
    
    age = data.get("age")
    if age is not None:
        try:
            age_num = int(age)
            today = date.today()
            return date(today.year - age_num, today.month, min(today.day, 28))
        except (ValueError, TypeError):
            pass
            
    today = date.today()
    return date(today.year - 30, 1, 1)

def create_patient(session: Session, user_id: Any, data: dict) -> PatientProfile:
    now = datetime.now(timezone.utc)
    uid = safe_uuid(user_id) or user_id
    user = user_crud.get_user(session, uid)
    if not user:
        raise ValueError("User not found")
        
    return user_crud.create_patient_profile(
        session=session,
        user_id=uid,
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        date_of_birth=calculate_dob(data),
        gender=data.get("gender", "Male"),
        blood_group=data.get("blood_type", data.get("blood_group", "O+")),
        medical_summary=data.get("medical_history", data.get("medical_summary", "")),
        created_at=now,
        updated_at=now
    )

def get_patient(session: Session, user_id: Any) -> Optional[PatientProfile]:
    uid = safe_uuid(user_id)
    if not uid:
        return None
    return user_crud.get_patient_profile(session, uid)

def update_patient(session: Session, user_id: Any, data: dict) -> Optional[PatientProfile]:
    uid = safe_uuid(user_id)
    if not uid:
        return None
    
    name = data.get("name", "")
    parts = name.split(" ", 1) if name else []
    first_name = data.get("first_name", parts[0] if len(parts) > 0 else "")
    last_name = data.get("last_name", parts[1] if len(parts) > 1 else "")
    dob = calculate_dob(data)
    
    profile = user_crud.get_patient_profile(session, uid)
    now = datetime.now(timezone.utc)
    
    if not profile:
        return user_crud.create_patient_profile(
            session=session,
            user_id=uid,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            gender=data.get("gender", "Male"),
            blood_group=data.get("blood_type", data.get("blood_group", "O+")),
            medical_summary=data.get("medical_history", data.get("medical_summary", "")),
            created_at=now,
            updated_at=now
        )
    else:
        if first_name:
            profile.first_name = first_name
        if last_name:
            profile.last_name = last_name
        if dob:
            profile.date_of_birth = dob
        if "gender" in data and data["gender"]:
            profile.gender = data["gender"]
        if "blood_type" in data or "blood_group" in data:
            profile.blood_group = data.get("blood_type", data.get("blood_group"))
        if "medical_history" in data or "medical_summary" in data:
            profile.medical_summary = data.get("medical_history", data.get("medical_summary"))
        profile.updated_at = now
        session.commit()
        session.refresh(profile)
        return profile

def delete_patient(session: Session, user_id: Any) -> bool:
    from database.crud.utils import delete_record
    return delete_record(session, PatientProfile, user_id)

def get_all_patients(session: Session) -> List[PatientProfile]:
    from sqlalchemy import select
    return session.scalars(select(PatientProfile)).all()
