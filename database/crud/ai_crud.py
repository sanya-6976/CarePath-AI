from typing import Optional, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import AIAnalysis, Recommendation, CarePlan, FollowUp
from database.crud.utils import create_record, get_record, update_record

def create_analysis(session: Session, **kwargs) -> AIAnalysis:
    """Creates a new AI analysis record."""
    return create_record(session, AIAnalysis, **kwargs)

def create_recommendation(session: Session, **kwargs) -> Recommendation:
    """Creates a new recommendation linked to an analysis."""
    return create_record(session, Recommendation, **kwargs)

def create_care_plan(session: Session, **kwargs) -> CarePlan:
    """Creates a new care plan."""
    return create_record(session, CarePlan, **kwargs)

def get_user_care_plans(session: Session, user_id: Any, status: Optional[str] = None) -> List[CarePlan]:
    """Retrieves care plans for a user, optionally filtered by status."""
    stmt = select(CarePlan).where(CarePlan.user_id == user_id)
    if status:
        stmt = stmt.where(CarePlan.status == status)
    return list(session.scalars(stmt).all())

def get_care_plan_by_id(session: Session, plan_id: Any) -> Optional[CarePlan]:
    """Retrieves a care plan by plan_id."""
    return get_record(session, CarePlan, plan_id)

def update_care_plan_status(session: Session, plan_id: Any, status: str) -> Optional[CarePlan]:
    """Updates the status of a care plan, setting completed_at if completed."""
    kwargs = {"status": status}
    if status.lower() == "completed":
        kwargs["completed_at"] = datetime.utcnow()
    return update_record(session, CarePlan, plan_id, **kwargs)

def create_followup(session: Session, **kwargs) -> FollowUp:
    """Creates a new follow-up appointment or task."""
    return create_record(session, FollowUp, **kwargs)

def get_user_followups(session: Session, user_id: Any, status: Optional[str] = None) -> List[FollowUp]:
    """Retrieves follow-ups for a user, optionally filtered by status."""
    stmt = select(FollowUp).where(FollowUp.user_id == user_id)
    if status:
        stmt = stmt.where(FollowUp.status == status)
    return list(session.scalars(stmt).all())

def get_followup_by_id(session: Session, followup_id: Any) -> Optional[FollowUp]:
    """Retrieves a follow-up record by followup_id."""
    return get_record(session, FollowUp, followup_id)

def update_followup_status(session: Session, followup_id: Any, status: str, completed_date: Optional[datetime] = None) -> Optional[FollowUp]:
    """Updates status and completion date of a follow-up."""
    kwargs = {"status": status}
    if completed_date or status.lower() in ["completed", "done"]:
        kwargs["completed_date"] = completed_date or datetime.utcnow()
    return update_record(session, FollowUp, followup_id, **kwargs)

def get_user_analyses(session: Session, user_id: Any) -> List[AIAnalysis]:
    """Retrieves AI analyses for a user."""
    stmt = select(AIAnalysis).where(AIAnalysis.user_id == user_id).order_by(AIAnalysis.created_at.desc())
    return list(session.scalars(stmt).all())

def get_user_recommendations(session: Session, user_id: Any) -> List[Recommendation]:
    """Retrieves recommendations for a user."""
    stmt = select(Recommendation).where(Recommendation.user_id == user_id).order_by(Recommendation.created_at.desc())
    return list(session.scalars(stmt).all())


