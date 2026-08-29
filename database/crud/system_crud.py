from typing import Optional, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import Notification, Feedback, AgentRun, TimelineEvent, EvidenceRetrieval
from database.crud.utils import create_record

def create_notification(session: Session, **kwargs) -> Notification:
    """Creates a system notification for a user."""
    return create_record(session, Notification, **kwargs)

def create_feedback(session: Session, **kwargs) -> Feedback:
    """Records user feedback."""
    return create_record(session, Feedback, **kwargs)

def get_user_feedback(session: Session, user_id: Any) -> List[Feedback]:
    """Retrieves feedback entries associated with a user."""
    stmt = select(Feedback).where(Feedback.user_id == user_id).order_by(Feedback.created_at.desc())
    return list(session.scalars(stmt).all())


def create_agent_run(session: Session, **kwargs) -> AgentRun:
    """Logs the execution details of an AI agent."""
    return create_record(session, AgentRun, **kwargs)

def create_timeline_event(session: Session, **kwargs) -> TimelineEvent:
    """Creates an event on the patient's timeline."""
    return create_record(session, TimelineEvent, **kwargs)

def get_user_timeline_events(session: Session, user_id: Any, event_type: Optional[str] = None, limit: int = 50) -> List[TimelineEvent]:
    """Retrieves chronological timeline events for a user, newest first."""
    stmt = select(TimelineEvent).where(TimelineEvent.user_id == user_id)
    if event_type:
        stmt = stmt.where(TimelineEvent.event_type == event_type)
    stmt = stmt.order_by(TimelineEvent.event_date.desc()).limit(limit)
    return list(session.scalars(stmt).all())

def create_evidence(session: Session, **kwargs) -> EvidenceRetrieval:
    """Logs retrieved evidence used in agent reasoning."""
    return create_record(session, EvidenceRetrieval, **kwargs)

def get_user_evidence(session: Session, user_id: Any) -> List[EvidenceRetrieval]:
    """Retrieves all evidence logs linked to agent runs executed for a user."""
    stmt = (
        select(EvidenceRetrieval)
        .join(AgentRun, EvidenceRetrieval.run_id == AgentRun.run_id)
        .where(AgentRun.user_id == user_id)
        .order_by(EvidenceRetrieval.retrieval_timestamp.desc())
    )
    return list(session.scalars(stmt).all())

def get_evidence_by_run(session: Session, run_id: Any) -> List[EvidenceRetrieval]:
    """Retrieves evidence records associated with a specific agent run."""
    stmt = select(EvidenceRetrieval).where(EvidenceRetrieval.run_id == run_id)
    return list(session.scalars(stmt).all())

