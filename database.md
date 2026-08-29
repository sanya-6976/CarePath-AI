# 📘 CarePath AI Database Documentation

**Version:** 1.0.0  
**Author:** CarePath Engineering Team  
**Date:** August 5, 2026  
**Database Engine:** PostgreSQL (Supabase)  
**Storage Engine:** Supabase Storage  
**ORM:** SQLAlchemy 2.0  
**Status:** 🟢 Active / Production Ready  

---

## 2. Introduction

Welcome to the CarePath AI Database Developer Handbook. 

**Purpose:**
The CarePath AI database serves as the central nervous system for all patient profiles, medical histories, symptom intakes, and AI-generated clinical reasoning. It is designed to securely and efficiently handle complex medical relationships and AI workflows.

**Overall Architecture:**
The architecture relies on a clear separation of concerns. Relational data is strictly structured in PostgreSQL, while binary medical files (images, PDFs) are delegated entirely to object storage, with only metadata saved in the database.

**Technology Selection:**
- **PostgreSQL:** Selected for its robust schema enforcement, JSON/UUID native support, and industry-standard reliability in healthcare applications.
- **Supabase:** Chosen to provide a scalable, managed PostgreSQL instance out-of-the-box, alongside a perfectly integrated Storage layer and Realtime capabilities.
- **SQLAlchemy ORM:** Used to provide a strongly typed, Pythonic abstraction layer over SQL, preventing SQL injection and simplifying CRUD operations for developers.

**Design Philosophy:**
- *Immutability for AI:* AI reasoning (analyses, recommendations) is largely immutable to maintain a strict audit trail.
- *Decoupled Storage:* Never bloat the database with binary files.
- *Domain-Driven CRUD:* No massive files. Break operations into logical domains (Users, Clinical, AI, System).

---

## 3. Architecture Overview

### PostgreSQL Flow
```ascii
[ FastAPI Application ]
          ↓
   [ CRUD Modules ]
          ↓
[ SQLAlchemy Models ]
          ↓
   [ PostgreSQL ]
```

### Supabase Storage Flow
```ascii
[ FastAPI Application ]
          ↓
  [ Storage Module ]
          ↓
 [ Supabase Storage ]
```

**Separation of Concerns:** 
The database (PostgreSQL) is strictly for relational data, metadata, and state tracking. The storage layer (Supabase Storage) is strictly for unstructured binary blobs (MRI scans, X-rays, PDFs). This ensures database backups remain lean, queries remain lightning fast, and storage scales infinitely without degrading database performance.

---

## 4. Project Structure

The database directory is structured for maximum modularity.

```text
database/
├── __init__.py           # Exposes models, CRUD, connections, and storage
├── connections.py        # Initializes SQLAlchemy Engine, Sessions, and Supabase client
├── models.py             # SQLAlchemy Declarative Models mirroring the Postgres schema
├── storage.py            # Interfaces directly with Supabase Storage buckets
├── test_database.py      # E2E testing script for DB and Storage verification
└── crud/
    ├── __init__.py       # Exposes all CRUD methods cleanly
    ├── utils.py          # Highly reusable generic CRUD (Create, Read, Update, Delete)
    ├── user_crud.py      # Operations for Users, PatientProfile, FamilyMembers
    ├── clinical_crud.py  # Operations for Visits, Sessions, Symptoms, Meds, Files
    ├── ai_crud.py        # Operations for Analysis, Recommendations, Plans, FollowUps
    └── system_crud.py    # Operations for Notifications, Feedback, AgentRuns, Timelines
```

> [!NOTE]
> `models.py` is the absolute source of truth for Python data shapes. It maps directly to existing Postgres tables without altering them.

---

## 5. Database Tables

Below is the exhaustive documentation for every implemented table.

### 5.1 Users
**Purpose:** Stores authentication and identity information. Root table for all data.
- **Columns:** `user_id`, `email`, `password_hash`, `role`, `account_status`, `created_at`, `updated_at`, `last_login`
- **Primary Key:** `user_id` (UUID)
- **Used By:** Auth, Dashboard, Admin Panel
- **Referenced By:** `PatientProfile`, `MedicalFiles`, `Visits`, `AIAnalysis`, etc.
- **Workflow:** Register User → Create Record → Create PatientProfile

### 5.2 PatientProfile
**Purpose:** Stores all personal and medical profile info belonging to a patient.
- **Columns:** `user_id`, `first_name`, `last_name`, `date_of_birth`, `gender`, `height`, `weight`, `blood_group`, `profile_picture`, `emergency_contact`, `medical_summary`, `created_at`, `updated_at`
- **Primary Key:** `user_id` (Foreign Key to `Users`)
- **Used By:** Dashboard, AI Analysis
- **Workflow:** User Registered → Profile Created → AI can analyze history.

### 5.3 MedicalFiles
**Purpose:** Stores metadata for uploaded documents (X-rays, MRIs).
- **Columns:** `file_id`, `user_id`, `visit_id`, `file_name`, `storage_path`, `file_type`, `mime_type`, `file_size`, `upload_date`, `analysis_status`, `ocr_text`, `created_at`, `updated_at`
- **Primary Key:** `file_id`
- **Foreign Keys:** `user_id`, `visit_id`
- **Used By:** Upload API, Vision AI Pipeline
- **Notes:** Actual files live in Supabase Storage. This table tracks status.

### 5.4 SymptomSessions
**Purpose:** Represents a single symptom submission session to group multiple symptoms.
- **Columns:** `session_id`, `user_id`, `session_date`, `session_type`, `status`, `created_at`, `updated_at`
- **Primary Key:** `session_id`
- **Foreign Keys:** `user_id`
- **Used By:** Intake Agent, Clinical Reasoning
- **Workflow:** Start Session → Add Symptoms → Analyze Group

### 5.5 PatientSymptoms
**Purpose:** Stores every individual symptom reported by a patient in a session.
- **Columns:** `symptom_id`, `session_id`, `user_id`, `symptom_name`, `symptom_description`, `onset_date`, `severity`, `duration`, `location`, `associated_symptoms`, `created_at`, `updated_at`
- **Primary Key:** `symptom_id`
- **Foreign Keys:** `session_id`, `user_id`
- **Used By:** Clinical Reasoning Engine

### 5.6 AIAnalysis
**Purpose:** Stores the final medical reasoning generated by AI after combining all patient data.
- **Columns:** `analysis_id`, `user_id`, `session_id`, `analysis_type`, `findings`, `differential_list`, `confidence_score`, `risk_level`, `summary`, `evidence_sources`, `ai_model_version`, `execution_time`, `created_at`, `updated_at`
- **Primary Key:** `analysis_id`
- **Foreign Keys:** `user_id`, `session_id`
- **Referenced By:** `Recommendations`, `CarePlans`
- **Notes:** This is the core output of CarePath AI. It is immutable.

### 5.7 Recommendations
**Purpose:** Actionable specialist recommendations produced by AI.
- **Columns:** `recommendation_id`, `analysis_id`, `user_id`, `recommendation_type`, `specialist_type`, `title`, `description`, `confidence`, `urgency`, `rationale`, `expected_outcome`, `estimated_timeline`, `status`, `created_at`, `updated_at`
- **Primary Key:** `recommendation_id`
- **Foreign Keys:** `analysis_id`, `user_id`

### 5.8 CarePlans
**Purpose:** Stores personalized, actionable care plans.
- **Columns:** `plan_id`, `user_id`, `analysis_id`, `plan_name`, `plan_description`, `status`, `next_steps`, `appointment_prep`, `lifestyle_changes`, `monitoring_points`, `estimated_duration`, `priority`, `created_at`, `updated_at`, `completed_at`
- **Primary Key:** `plan_id`
- **Foreign Keys:** `user_id`, `analysis_id`

### 5.9 FollowUps
**Purpose:** Stores follow-up reminders, checkpoints, and reassessments.
- **Columns:** `followup_id`, `user_id`, `plan_id`, `followup_type`, `scheduled_date`, `description`, `purpose`, `status`, `completed_date`, `notes`, `created_at`, `updated_at`
- **Primary Key:** `followup_id`
- **Foreign Keys:** `user_id`, `plan_id`

### 5.10 Notifications
**Purpose:** System notifications shown to the patient.
- **Columns:** `notification_id`, `user_id`, `notification_type`, `title`, `message`, `priority`, `related_record_id`, `related_record_type`, `is_read`, `delivery_channel`, `sent_at`, `read_at`, `created_at`
- **Primary Key:** `notification_id`
- **Foreign Keys:** `user_id`

### 5.11 Medications
**Purpose:** Stores medications prescribed or recommended.
- **Columns:** `medication_id`, `user_id`, `medication_name`, `dosage`, `frequency`, `duration`, `route`, `start_date`, `end_date`, `purpose`, `side_effects`, `instructions`, `prescribed_by`, `status`, `created_at`, `updated_at`
- **Primary Key:** `medication_id`
- **Foreign Keys:** `user_id`

### 5.12 Visits
**Purpose:** Stores consultations, appointments, and hospital visits.
- **Columns:** `visit_id`, `user_id`, `visit_type`, `provider_name`, `facility_name`, `visit_date`, `duration`, `visit_reason`, `notes`, `outcome`, `next_appointment`, `status`, `created_at`, `updated_at`
- **Primary Key:** `visit_id`
- **Foreign Keys:** `user_id`

### 5.13 FamilyMembers
**Purpose:** Defines relationships between users for family healthcare management.
- **Columns:** `family_id`, `primary_user_id`, `member_user_id`, `relationship`, `access_level`, `notes`, `status`, `created_at`, `updated_at`
- **Primary Key:** `family_id`
- **Foreign Keys:** `primary_user_id`, `member_user_id`

### 5.14 Feedback
**Purpose:** Stores user ratings and feedback to improve AI reasoning.
- **Columns:** `feedback_id`, `user_id`, `feedback_type`, `rating`, `title`, `message`, `related_record_id`, `related_record_type`, `status`, `response`, `created_at`, `updated_at`
- **Primary Key:** `feedback_id`
- **Foreign Keys:** `user_id`

### 5.15 AuditHistory
**Purpose:** Immutable record of important system actions for compliance.
- **Columns:** `audit_id`, `user_id`, `action_type`, `record_type`, `record_id`, `old_values`, `new_values`, `ip_address`, `user_agent`, `reason`, `status`, `error_message`, `created_at`
- **Primary Key:** `audit_id`
- **Foreign Keys:** `user_id`

### 5.16 PromptTemplates
**Purpose:** Version-controlled prompts used by AI agents.
- **Columns:** `template_id`, `agent_name`, `template_version`, `template_name`, `template_content`, `template_description`, `is_active`, `performance_metrics`, `created_by`, `created_at`, `updated_at`
- **Primary Key:** `template_id`

### 5.17 AgentRuns
**Purpose:** Execution history of AI agents (inputs, outputs, tokens, costs).
- **Columns:** `run_id`, `user_id`, `agent_name`, `agent_version`, `template_id`, `input_data`, `output_data`, `execution_time`, `token_count`, `cost`, `status`, `error_message`, `model_used`, `created_at`
- **Primary Key:** `run_id`
- **Foreign Keys:** `user_id`, `template_id`

### 5.18 TimelineEvents
**Purpose:** Chronological medical events for building the patient's healthcare timeline.
- **Columns:** `event_id`, `user_id`, `event_type`, `event_date`, `event_title`, `event_description`, `severity`, `related_record_id`, `related_record_type`, `visible_to_patient`, `created_at`
- **Primary Key:** `event_id`
- **Foreign Keys:** `user_id`

### 5.19 EvidenceRetrieval
**Purpose:** Stores evidence retrieved by the RAG pipeline to support AI recommendations.
- **Columns:** `evidence_id`, `run_id`, `source_type`, `source_reference`, `evidence_text`, `relevance_score`, `retrieval_timestamp`, `context_used_in`, `created_at`
- **Primary Key:** `evidence_id`
- **Foreign Keys:** `run_id`

---

## 6. Entity Relationship Overview

The relationships are strictly enforced at the PostgreSQL layer and navigated seamlessly using SQLAlchemy ORM.

### High-Level ER Diagram

```ascii
                      +-------------------+
                      |   PromptTemplates |
                      +---------+---------+
                                |
                                v
+---------------+     +-------------------+     +-------------------+
| PatientProfile|<----|      Users        |---->|   FamilyMembers   |
+---------------+     +----+----+----+----+     +-------------------+
                           |    |    |
           +---------------+    |    +---------------+
           |                    |                    |
           v                    v                    v
+---------------+     +-------------------+     +-------------------+
| SymptomSession|     |      Visits       |     |   MedicalFiles    |
+-------+-------+     +---------+---------+     +---------+---------+
        |                       |                         |
        v                       v                         |
+---------------+     +-------------------+               |
|PatientSymptoms|     |   TimelineEvents  |<--------------+
+-------+-------+     +-------------------+
        |
        v
+-------------------------------------------------------------+
|                         AIAnalysis                          |
+----+-------------------+-------------------------+----------+
     |                   |                         |
     v                   v                         v
+---------+    +-------------------+     +--------------------+
|CarePlans|    |  Recommendations  |     | EvidenceRetrieval  |
+----+----+    +-------------------+     +--------------------+
     |                   |
     v                   v
+---------+    +-------------------+
|FollowUps|    |   Notifications   |
+---------+    +-------------------+
```

---

## 7. CRUD Layer

**Why CRUD Exists:**
Directly querying models inside FastAPI routers leads to spaghetti code. The CRUD layer encapsulates the database logic, ensuring transactions are safely committed or rolled back. 

**Module Organization:**
- `user_crud.py`: Manages user identity, patient profiles, and family links.
- `clinical_crud.py`: Manages real-world medical touchpoints (Visits, Files, Symptoms).
- `ai_crud.py`: Manages AI-generated artifacts (Analysis, Care Plans, Follow Ups).
- `system_crud.py`: Manages background/system logs (Notifications, Timelines, Audits).
- `utils.py`: Centralizes boilerplate `session.add`, `session.commit`, `session.rollback` logic to prevent repetitive code.

**Example Usage:**
```python
from database import crud
from database.connections import SessionLocal

session = SessionLocal()
try:
    user = crud.create_user(
        session=session,
        email="patient@carepath.ai",
        password_hash="hashed_pw",
        role="patient",
        account_status="active"
    )
finally:
    session.close()
```

---

## 8. Storage Layer

**Why Separate Storage?**
PostgreSQL is optimized for structured data indexing and querying. Storing heavy binaries (like a 50MB MRI scan) in the database degrades backup speeds, increases costs, and ruins query performance. 

**Upload Pipeline Workflow:**
```ascii
[ User Uploads File ]
          ↓
[ FastAPI receives File ]
          ↓
[ Supabase Storage API saves to Bucket ]
          ↓ Returns Public URL & Path
[ CRUD Layer saves metadata to PostgreSQL ]
          ↓
[ AI processing triggered on MedicalFiles row ]
```

---

## 9. ORM Layer

- **SQLAlchemy Models:** Written in `models.py`, inheriting from `Base`.
- **Relationships:** Used strictly for navigation in Python (e.g., `user.medical_files`), mirroring PostgreSQL foreign keys.
- **Sessions:** Used to bind the Python runtime to the database connection pool.
- **Transactions:** Handled safely in `crud/utils.py`. If an error occurs, `session.rollback()` is automatically called.
- **UUID Handling:** Handled natively by PostgreSQL.
- **Timestamp Handling:** Managed via `datetime.now(timezone.utc)`.

---

## 10. Connection Layer

The `database/connections.py` file manages connectivity.

**Environment Variables Required (`.env`):**
- `DATABASE_URL`: Connection string for PostgreSQL (SQLAlchemy uses this).
- `SUPABASE_URL`: API URL for Supabase Storage.
- `SUPABASE_KEY`: `anon` or `service_role` key for Storage API.

**Core Components:**
- `engine`: SQLAlchemy Engine managing the connection pool.
- `SessionLocal`: Factory for generating isolated session workers.
- `Base`: Declarative base for models.
- `supabase`: Initialized client for the Storage API.

---

## 11. Developer Guide

**Uploading a File & Saving to DB:**
```python
from datetime import datetime, timezone
from database import crud, storage
from database.connections import SessionLocal

session = SessionLocal()

# 1. Upload to Supabase Storage
upload_metadata = storage.upload_file("local_xray.png", "medical_files/user123/xray.png")

# 2. Save to Postgres
crud.create_medical_file(
    session=session,
    file_id=uuid.uuid4(),
    user_id=user123,
    file_name="local_xray.png",
    storage_path=upload_metadata["storage_path"],
    file_type="image/png",
    mime_type="image/png",
    file_size=upload_metadata["file_size"],
    upload_date=datetime.now(timezone.utc),
    analysis_status="pending",
    created_at=datetime.now(timezone.utc)
)
```

---

## 12. Demo Upload Flow

The repository includes a script: `demo_upload_flow.py`

**Purpose:** Provides a working E2E example of generating a file, uploading it to Supabase Storage, recording it in Postgres, and cleaning it up.

**Stages:**
1. **Local File:** Generates a dummy file (`demo_xray.jpg`).
2. **Prerequisites:** Creates a fake User and Visit in DB.
3. **Storage Upload:** Uploads file using `storage.py`.
4. **Metadata:** Uses `crud.create_medical_file()` to save the URL.
5. **Cleanup:** *Critical.* Deletes the DB records and Storage file to prevent garbage data during development testing.

---

## 13. Testing

The repository includes a script: `test_database.py`

**What it tests:**
- **Connection:** Validates `SessionLocal`.
- **CRUD Insert/Read/Update/Delete:** Tests the `utils.py` transaction flows.
- **Storage Testing:** Verifies upload and deletion from Supabase buckets.
- **Cleanup:** Asserts that database state is restored exactly as it was.

Run with: `python -m database.test_database`

---

## 14. Security

> [!CAUTION]
> Never commit your `.env` file containing database URLs or Supabase keys.

- **Password Hashing:** `password_hash` column NEVER stores plain text.
- **Environment Variables:** Loaded strictly via `dotenv` and ignored in `.gitignore`.
- **Storage Permissions:** Managed via Supabase RLS (Row Level Security) policies on the bucket.
- **Database Permissions:** PostgreSQL handles access controls based on the connection string user.

---

## 15. Best Practices

> [!TIP]
> - **Always use CRUD:** Never write `session.add()` directly in a router.
> - **Never write raw SQL:** Always use SQLAlchemy syntax (`select()`, `session.get()`).
> - **Always use UUIDs:** Rely on the `uuid` package.
> - **Use Timezone-Aware Dates:** `datetime.now(timezone.utc)` is required.
> - **Cleanup:** Always delete test data in dev scripts.

---

## 16. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `psycopg2.OperationalError` | Database connection failure. | Verify `DATABASE_URL` in `.env` and check internet/VPN. |
| `ModuleNotFoundError: No module named 'database'` | Python path issue. | Run scripts as a module: `python -m database.test_database`. |
| `NotNullViolation` | Missing required column. | Check the DB Schema in `models.py`. Pass all non-nullable fields (e.g., `created_at`, `updated_at`). |
| `StorageException` | Supabase API failure. | Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`. |

---

## 17. Future Improvements

*These are architectural concepts for future scalability, not currently implemented.*

- **Database Indexing:** Adding B-Tree indexes on `user_id` and `created_at` across heavy tables.
- **Caching:** Implementing Redis for frequently accessed `PatientProfiles`.
- **Partitioning:** Splitting `AgentRuns` or `AuditHistory` by month.
- **Backups:** Configuring automated Supabase PITR (Point in Time Recovery).
- **Performance Monitoring:** Connecting `pg_stat_statements` to Datadog.

---

## 18. Appendix

- **Folder Structure:** See Section 4.
- **Dependencies:** `sqlalchemy`, `psycopg2-binary`, `supabase`, `python-dotenv`
- **Useful Commands:**
  - Test DB: `python -m database.test_database`
  - Demo Flow: `python demo_upload_flow.py`
