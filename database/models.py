from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, Numeric, BigInteger, ForeignKey
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.connections import Base

class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255))
    password_hash = Column(Text)
    role = Column(String(20))
    account_status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_login = Column(DateTime)

    # Relationships
    profile = relationship("PatientProfile", back_populates="user", uselist=False)
    visits = relationship("Visit", back_populates="user")
    symptom_sessions = relationship("SymptomSession", back_populates="user")
    ai_analyses = relationship("AIAnalysis", back_populates="user")
    medical_files = relationship("MedicalFile", back_populates="user")
    patient_symptoms = relationship("PatientSymptom", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    care_plans = relationship("CarePlan", back_populates="user")
    follow_ups = relationship("FollowUp", back_populates="user")
    medications = relationship("Medication", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    companion_conversations = relationship("CompanionConversation", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")

class PatientProfile(Base):
    __tablename__ = 'patient_profiles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    height = Column(Numeric(5, 2))
    weight = Column(Numeric(5, 2))
    blood_group = Column(String(5))
    profile_picture = Column(Text)
    emergency_contact = Column(String(20))
    medical_summary = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="profile")

class FamilyMember(Base):
    __tablename__ = 'family_members'

    family_id = Column(UUID(as_uuid=True), primary_key=True)
    primary_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    member_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    relationship_type = Column('relationship', String(20))
    access_level = Column(String(20))
    notes = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    primary_user = relationship("User", foreign_keys=[primary_user_id])
    member_user = relationship("User", foreign_keys=[member_user_id])

class Visit(Base):
    __tablename__ = 'visits'

    visit_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    visit_type = Column(String(30))
    provider_name = Column(String(255))
    facility_name = Column(String(255))
    visit_date = Column(DateTime)
    duration = Column(Integer)
    visit_reason = Column(Text)
    notes = Column(Text)
    outcome = Column(Text)
    next_appointment = Column(DateTime)
    status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="visits")
    medical_files = relationship("MedicalFile", back_populates="visit")

class SymptomSession(Base):
    __tablename__ = 'symptom_sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    session_date = Column(DateTime)
    session_type = Column(String(20))
    status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="symptom_sessions")
    symptoms = relationship("PatientSymptom", back_populates="session")
    analyses = relationship("AIAnalysis", back_populates="session")

class PatientSymptom(Base):
    __tablename__ = 'patient_symptoms'

    symptom_id = Column(UUID(as_uuid=True), primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('symptom_sessions.session_id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    symptom_name = Column(String(255))
    symptom_description = Column(Text)
    onset_date = Column(Date)
    severity = Column(String(20))
    duration = Column(String(100))
    location = Column(String(255))
    associated_symptoms = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="patient_symptoms")
    session = relationship("SymptomSession", back_populates="symptoms")

class Medication(Base):
    __tablename__ = 'medications'

    medication_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    medication_name = Column(String(255))
    dosage = Column(String(100))
    frequency = Column(String(100))
    duration = Column(String(100))
    route = Column(String(20))
    start_date = Column(Date)
    end_date = Column(Date)
    purpose = Column(Text)
    side_effects = Column(Text)
    instructions = Column(Text)
    prescribed_by = Column(String(255))
    status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="medications")

class MedicalFile(Base):
    __tablename__ = 'medical_files'

    file_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    visit_id = Column(UUID(as_uuid=True), ForeignKey('visits.visit_id'))
    file_name = Column(String(255))
    storage_path = Column(Text)
    file_type = Column(String(50))
    mime_type = Column(String(100))
    file_size = Column(BigInteger)
    upload_date = Column(DateTime)
    analysis_status = Column(String(20))
    ocr_text = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="medical_files")
    visit = relationship("Visit", back_populates="medical_files")

class AIAnalysis(Base):
    __tablename__ = 'ai_analysis'

    analysis_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    session_id = Column(UUID(as_uuid=True), ForeignKey('symptom_sessions.session_id'))
    analysis_type = Column(String(50))
    findings = Column(Text)
    differential_list = Column(Text)
    confidence_score = Column(Numeric(3, 2))
    risk_level = Column(String(20))
    summary = Column(Text)
    evidence_sources = Column(Text)
    ai_model_version = Column(String(100))
    execution_time = Column(Integer)

    previous_analysis_id = Column(UUID(as_uuid=True), ForeignKey('ai_analysis.analysis_id'), nullable=True)
    changed_factors = Column(Text, nullable=True)
    new_information = Column(Text, nullable=True)
    missing_information = Column(Text, nullable=True)
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="ai_analyses")
    session = relationship("SymptomSession", back_populates="analyses")
    recommendations = relationship("Recommendation", back_populates="analysis")
    care_plans = relationship("CarePlan", back_populates="analysis")
    previous_analysis = relationship("AIAnalysis", remote_side=[analysis_id], backref="next_analyses")

class PatientUpdate(Base):
    __tablename__ = 'patient_updates'

    update_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    update_type = Column(String(50)) # symptom, medication, document, free_text
    content = Column(Text)
    created_at = Column(DateTime)
    
    user = relationship("User")

class Recommendation(Base):
    __tablename__ = 'recommendations'

    recommendation_id = Column(UUID(as_uuid=True), primary_key=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('ai_analysis.analysis_id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    recommendation_type = Column(String(30))
    specialist_type = Column(String(100))
    title = Column(String(255))
    description = Column(Text)
    confidence = Column(Numeric(3, 2))
    urgency = Column(String(20))
    rationale = Column(Text)
    expected_outcome = Column(Text)
    estimated_timeline = Column(String(100))
    status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="recommendations")
    analysis = relationship("AIAnalysis", back_populates="recommendations")

class CarePlan(Base):
    __tablename__ = 'care_plans'

    plan_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('ai_analysis.analysis_id'))
    plan_name = Column(String(255))
    plan_description = Column(Text)
    status = Column(String(20))
    next_steps = Column(Text)
    appointment_prep = Column(Text)
    lifestyle_changes = Column(Text)
    monitoring_points = Column(Text)
    estimated_duration = Column(String(100))
    priority = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="care_plans")
    analysis = relationship("AIAnalysis", back_populates="care_plans")
    follow_ups = relationship("FollowUp", back_populates="care_plan")

class FollowUp(Base):
    __tablename__ = 'follow_ups'

    followup_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    plan_id = Column(UUID(as_uuid=True), ForeignKey('care_plans.plan_id'))
    followup_type = Column(String(20))
    scheduled_date = Column(DateTime)
    description = Column(Text)
    purpose = Column(Text)
    status = Column(String(20))
    completed_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="follow_ups")
    care_plan = relationship("CarePlan", back_populates="follow_ups")

class Feedback(Base):
    __tablename__ = 'feedback'

    feedback_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    feedback_type = Column(String(30))
    rating = Column(Integer)
    title = Column(String(255))
    message = Column(Text)
    related_record_id = Column(UUID(as_uuid=True))
    related_record_type = Column(String(50))
    status = Column(String(20))
    response = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="feedback")

class Notification(Base):
    __tablename__ = 'notifications'

    notification_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    notification_type = Column(String(20))
    title = Column(String(255))
    message = Column(Text)
    priority = Column(String(20))
    related_record_id = Column(UUID(as_uuid=True))
    related_record_type = Column(String(50))
    is_read = Column(Boolean)
    delivery_channel = Column(String(20))
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    created_at = Column(DateTime)

    user = relationship("User", back_populates="notifications")

class PromptTemplate(Base):
    __tablename__ = 'prompt_templates'

    template_id = Column(UUID(as_uuid=True), primary_key=True)
    agent_name = Column(String(100))
    template_version = Column(String(20))
    template_name = Column(String(255))
    template_content = Column(Text)
    template_description = Column(Text)
    is_active = Column(Boolean)
    performance_metrics = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    creator = relationship("User")

class AuditHistory(Base):
    __tablename__ = 'audit_history'

    audit_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    action_type = Column(String(20))
    record_type = Column(String(100))
    record_id = Column(UUID(as_uuid=True))
    old_values = Column(Text)
    new_values = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    reason = Column(Text)
    status = Column(String(20))
    error_message = Column(Text)
    created_at = Column(DateTime)

    user = relationship("User")

class AgentRun(Base):
    __tablename__ = 'agent_runs'

    run_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    agent_name = Column(String(100))
    agent_version = Column(String(20))
    template_id = Column(UUID(as_uuid=True), ForeignKey('prompt_templates.template_id'))
    input_data = Column(Text)
    output_data = Column(Text)
    execution_time = Column(Integer)
    token_count = Column(Integer)
    cost = Column(Numeric(10, 4))
    status = Column(String(20))
    error_message = Column(Text)
    model_used = Column(String(100))
    created_at = Column(DateTime)

    user = relationship("User")
    template = relationship("PromptTemplate")

class TimelineEvent(Base):
    __tablename__ = 'timeline_events'

    event_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    event_type = Column(String(20))
    event_date = Column(DateTime)
    event_title = Column(String(255))
    event_description = Column(Text)
    severity = Column(String(20))
    related_record_id = Column(UUID(as_uuid=True))
    related_record_type = Column(String(50))
    visible_to_patient = Column(Boolean)
    created_at = Column(DateTime)

    user = relationship("User")

class EvidenceRetrieval(Base):
    __tablename__ = 'evidence_retrieval'

    evidence_id = Column(UUID(as_uuid=True), primary_key=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey('agent_runs.run_id'))
    source_type = Column(String(30))
    source_reference = Column(Text)
    evidence_text = Column(Text)
    relevance_score = Column(Numeric(3, 2))
    retrieval_timestamp = Column(DateTime)
    context_used_in = Column(String(100))
    created_at = Column(DateTime)

    agent_run = relationship("AgentRun")

# Patient-facing companion memory is deliberately separate from the medical record.
class CompanionConversation(Base):
    __tablename__ = 'companion_conversations'

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="companion_conversations")
    messages = relationship("CompanionMessage", back_populates="conversation", cascade="all, delete-orphan")

class CompanionMessage(Base):
    __tablename__ = 'companion_messages'

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('companion_conversations.conversation_id'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    language = Column(String(8), nullable=False, default='en')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation = relationship("CompanionConversation", back_populates="messages")

class UserPreference(Base):
    __tablename__ = 'user_preferences'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), primary_key=True)
    language = Column(String(8), nullable=False, default='en')
    voice_responses = Column(Boolean, nullable=False, default=False)
    use_carepath_history = Column(Boolean, nullable=False, default=True)
    simple_medical_terms = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="preferences")
