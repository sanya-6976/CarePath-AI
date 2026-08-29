// Authentication & User types
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role?: string;
  created_at?: string;
}

export interface AuthResponse {
  token: string;
  user: UserProfile;
  patient_id?: string;
}

// Patient profile details
export interface Patient {
  id: string;
  user_id: string;
  name: string;
  age: number;
  gender: string;
  blood_type?: string;
  allergies?: string[];
  medical_history?: string;
  current_symptoms?: string;
  created_at?: string;
  updated_at?: string;
}

// Medical Record
export type RecordType = 'image' | 'report' | 'prescription';

export interface MedicalRecord {
  id: string;
  patient_id: string;
  title: string;
  type: RecordType;
  file_url: string;
  file_name?: string;
  created_at: string;
  summary?: string;
}

// Agent names in the multi-agent backend analysis pipeline
export type AgentName =
  | 'Supervisor'
  | 'Intake'
  | 'Vision'
  | 'Docs'
  | 'Timeline'
  | 'Evidence'
  | 'Clinical Reasoning'
  | 'Safety'
  | 'Referral'
  | 'Care Plan'
  | 'Follow-up';

export interface AgentState {
  status: 'idle' | 'running' | 'completed' | 'failed';
  message?: string;
  updated_at?: string;
}

// Detailed analysis payload
export interface AnalysisResult {
  id: string;
  patient_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  agent_states?: Record<AgentName, AgentState>;
  specialist_recommendation?: string;
  explanation?: string;
  considered_factors?: string[];
  safety_alerts?: string[];
  created_at: string;
}

// Journey / Timeline events
export type TimelineEventType =
  | 'symptom'
  | 'upload'
  | 'analysis'
  | 'referral'
  | 'followup'
  | 'consultation';

export interface TimelineEvent {
  id: string;
  patient_id: string;
  type: TimelineEventType;
  title: string;
  description: string;
  details?: string;
  timestamp: string;
}

// Follow-up check-ins
export interface FollowUp {
  id: string;
  patient_id: string;
  check_in_date: string;
  status: 'pending' | 'completed';
  notes?: string;
  symptoms_logged?: string;
  created_at: string;
}

// Notifications
export interface AppNotification {
  id: string;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}
