import os
import sys
import uuid
import mimetypes
import random
from datetime import datetime, timezone, timedelta

# Add parent directory to path so 'database' module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connections import SessionLocal, supabase, engine
from database import crud
from database import storage
from database.models import (
    User, Visit, MedicalFile, PatientSymptom, SymptomSession, 
    Medication, AIAnalysis, Recommendation
)
from sqlalchemy import text

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress Enter to continue...")

def print_header(title):
    clear_screen()
    print("======================================================")
    print(f"           {title}")
    print("======================================================\n")

def get_session():
    return SessionLocal()

def get_utc_now():
    return datetime.now(timezone.utc)

# ==========================================
# 1. Patient Management
# ==========================================
def create_patient(session):
    print_header("Create Patient")
    email = input("Email: ")
    if not email:
        print("❌ Email is required.")
        return
        
    try:
        now = get_utc_now()
        user_id = uuid.uuid4()
        user = crud.create_user(
            session=session,
            user_id=user_id,
            email=email,
            password_hash="dev_hash_123",
            role="patient",
            account_status="active",
            created_at=now,
            updated_at=now
        )
        print(f"\n✅ Patient created successfully!")
        print(f"UUID: {user.user_id}")
    except Exception as e:
        print(f"\n❌ Error creating patient: {e}")

def list_patients(session):
    print_header("List Patients")
    users = session.query(User).filter(User.role == 'patient').all()
    if not users:
        print("No patients found.")
    else:
        for u in users:
            print(f"[{u.user_id}] - {u.email} ({u.account_status})")

def patient_management():
    while True:
        print_header("Patient Management")
        print("1. Create Patient")
        print("2. List Patients")
        print("3. Back to Main Menu")
        choice = input("\nSelect an option: ")
        
        session = get_session()
        try:
            if choice == '1':
                create_patient(session)
                pause()
            elif choice == '2':
                list_patients(session)
                pause()
            elif choice == '3':
                break
        finally:
            session.close()

# ==========================================
# 2. Visit Management
# ==========================================
def create_visit(session):
    print_header("Create Visit")
    users = session.query(User).filter(User.role == 'patient').all()
    if not users:
        print("❌ No patients exist. Create a patient first.")
        return
        
    for i, u in enumerate(users):
        print(f"{i+1}. {u.email} ({u.user_id})")
        
    try:
        user_idx = int(input("\nSelect Patient # (0 to cancel): ")) - 1
        if user_idx == -1: return
        selected_user = users[user_idx]
        
        visit_type = input("Visit Type (consultation/appointment): ") or "consultation"
        reason = input("Reason: ")
        
        now = get_utc_now()
        visit = crud.create_visit(
            session=session,
            visit_id=uuid.uuid4(),
            user_id=selected_user.user_id,
            visit_type=visit_type,
            visit_reason=reason,
            visit_date=now,
            status="completed",
            created_at=now,
            updated_at=now
        )
        print(f"\n✅ Visit created successfully!")
        print(f"UUID: {visit.visit_id}")
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_visits(session):
    print_header("List Visits")
    visits = session.query(Visit).all()
    if not visits:
        print("No visits found.")
    else:
        for v in visits:
            print(f"[{v.visit_id}] - User: {v.user_id} - Type: {v.visit_type} - Date: {v.visit_date}")

def visit_management():
    while True:
        print_header("Visit Management")
        print("1. Create Visit")
        print("2. List Visits")
        print("3. Back to Main Menu")
        choice = input("\nSelect an option: ")
        
        session = get_session()
        try:
            if choice == '1':
                create_visit(session)
                pause()
            elif choice == '2':
                list_visits(session)
                pause()
            elif choice == '3':
                break
        finally:
            session.close()

# ==========================================
# 3. Medical File Upload
# ==========================================
def upload_medical_file():
    session = get_session()
    try:
        print_header("Medical File Upload")
        
        users = session.query(User).filter(User.role == 'patient').all()
        if not users:
            print("❌ No patients exist.")
            pause()
            return
            
        print("--- 1. Select Patient ---")
        for i, u in enumerate(users):
            print(f"{i+1}. {u.email}")
            
        try:
            u_idx = int(input("\nSelect Patient #: ")) - 1
            selected_user = users[u_idx]
        except:
            print("❌ Invalid selection."); pause(); return
            
        print("\n--- 2. Select Visit ---")
        visits = session.query(Visit).filter(Visit.user_id == selected_user.user_id).all()
        selected_visit_id = None
        
        if visits:
            print("0. No Visit")
            for i, v in enumerate(visits):
                print(f"{i+1}. [Date: {v.visit_date}] {v.visit_reason}")
            try:
                v_idx = int(input("\nSelect Visit #: "))
                if v_idx > 0:
                    selected_visit_id = visits[v_idx-1].visit_id
            except:
                print("❌ Invalid selection."); pause(); return
        else:
            print("No visits found. Proceeding without visit.")
            
        # 3. File Path
        file_path = input("\n--- 3. Ask for file path ---\nEnter absolute path to file: ").strip('\"\' ')
        if not os.path.exists(file_path):
            print("❌ File does not exist.")
            pause(); return
            
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type: mime_type = "application/octet-stream"
        file_size = os.path.getsize(file_path)
        
        print(f"\n--- 5. File Verified ---")
        print(f"Filename: {file_name}")
        print(f"MIME Type: {mime_type}")
        print(f"File Size: {file_size} bytes")
        
        # 6. Upload
        print(f"\n--- 6. Uploading file to Supabase... ---")
        file_id = uuid.uuid4()
        storage_dest = f"medical_files/{selected_user.user_id}/{file_id}_{file_name}"
        
        try:
            upload_meta = storage.upload_file(file_path, storage_dest)
        except Exception as e:
            print(f"❌ Storage upload failed: {e}")
            pause(); return
            
        # 8. Insert Metadata
        print("\n--- 8. Saving metadata to PostgreSQL... ---")
        now = get_utc_now()
        medical_file = crud.create_medical_file(
            session=session,
            file_id=file_id,
            user_id=selected_user.user_id,
            visit_id=selected_visit_id,
            file_name=file_name,
            storage_path=upload_meta['storage_path'],
            file_type=mime_type,
            mime_type=mime_type,
            file_size=file_size,
            upload_date=now,
            analysis_status="pending",
            created_at=now,
            updated_at=now
        )
        
        # 9. Display
        print("\n--- 9. Result ---")
        print(f"✅ File Uploaded & Saved!")
        print(f"Medical File ID: {medical_file.file_id}")
        print(f"Storage Path:    {upload_meta['storage_path']}")
        print(f"Public URL:      {upload_meta['public_url']}")
        print(f"Upload Status:   Success")
        pause()
        
    finally:
        session.close()

# ==========================================
# 4. Symptom Management
# ==========================================
def symptom_management():
    while True:
        print_header("Symptom Management")
        print("1. Create Symptom Session")
        print("2. Add Symptoms")
        print("3. View Symptoms")
        print("4. Back")
        
        choice = input("\nSelect an option: ")
        session = get_session()
        try:
            if choice == '1':
                users = session.query(User).filter(User.role == 'patient').all()
                if not users:
                    print("❌ No patients exist."); pause(); continue
                for i, u in enumerate(users):
                    print(f"{i+1}. {u.email}")
                u_idx = int(input("\nSelect Patient #: ")) - 1
                now = get_utc_now()
                sess = crud.create_session(
                    session=session,
                    session_id=uuid.uuid4(),
                    user_id=users[u_idx].user_id,
                    session_date=now,
                    session_type="initial",
                    status="in_progress",
                    created_at=now,
                    updated_at=now
                )
                print(f"✅ Session created! ID: {sess.session_id}")
                pause()
                
            elif choice == '2':
                sessions = session.query(SymptomSession).all()
                if not sessions:
                    print("❌ No symptom sessions exist."); pause(); continue
                for i, s in enumerate(sessions):
                    print(f"{i+1}. {s.session_id} (User: {s.user_id})")
                s_idx = int(input("\nSelect Session #: ")) - 1
                selected_sess = sessions[s_idx]
                
                name = input("Symptom Name: ")
                desc = input("Description: ")
                severity = input("Severity (mild/moderate/severe/critical): ") or "moderate"
                duration = input("Duration: ")
                location = input("Location: ")
                
                now = get_utc_now()
                symp = crud.create_symptom(
                    session=session,
                    symptom_id=uuid.uuid4(),
                    session_id=selected_sess.session_id,
                    user_id=selected_sess.user_id,
                    symptom_name=name,
                    symptom_description=desc,
                    severity=severity,
                    duration=duration,
                    location=location,
                    onset_date=now,
                    created_at=now,
                    updated_at=now
                )
                print(f"✅ Symptom added! ID: {symp.symptom_id}")
                pause()
                
            elif choice == '3':
                symptoms = session.query(PatientSymptom).all()
                for s in symptoms:
                    print(f"[{s.symptom_id}] {s.symptom_name} - {s.severity}")
                pause()
            elif choice == '4':
                break
        except Exception as e:
            print(f"❌ Error: {e}")
            pause()
        finally:
            session.close()

# ==========================================
# 5. Medication Management
# ==========================================
def medication_management():
    while True:
        print_header("Medication Management")
        print("1. Create Medication")
        print("2. View Medications")
        print("3. Back")
        
        choice = input("\nSelect an option: ")
        session = get_session()
        try:
            if choice == '1':
                users = session.query(User).filter(User.role == 'patient').all()
                if not users:
                    print("❌ No patients exist."); pause(); continue
                for i, u in enumerate(users):
                    print(f"{i+1}. {u.email}")
                u_idx = int(input("\nSelect Patient #: ")) - 1
                user_id = users[u_idx].user_id
                
                name = input("Medication Name: ")
                dosage = input("Dosage: ")
                freq = input("Frequency: ")
                
                now = get_utc_now()
                med = crud.clinical_crud.create_medication(
                    session=session,
                    medication_id=uuid.uuid4(),
                    user_id=user_id,
                    medication_name=name,
                    dosage=dosage,
                    frequency=freq,
                    route="Oral",
                    start_date=now.date(),
                    purpose="Demo",
                    status="active",
                    created_at=now,
                    updated_at=now
                )
                print(f"✅ Medication created! ID: {med.medication_id}")
                pause()
            elif choice == '2':
                meds = session.query(Medication).all()
                for m in meds:
                    print(f"[{m.medication_id}] {m.medication_name} ({m.dosage})")
                pause()
            elif choice == '3':
                break
        except Exception as e:
            print(f"❌ Error: {e}")
            pause()
        finally:
            session.close()

# ==========================================
# 6. Database Viewer
# ==========================================
def database_viewer():
    session = get_session()
    try:
        print_header("Database Viewer")
        print(f"Users: {session.query(User).count()}")
        print(f"Visits: {session.query(Visit).count()}")
        print(f"Medical Files: {session.query(MedicalFile).count()}")
        print(f"Symptoms: {session.query(PatientSymptom).count()}")
        print(f"AI Analyses: {session.query(AIAnalysis).count()}")
        print(f"Recommendations: {session.query(Recommendation).count()}")
    finally:
        session.close()
    pause()

# ==========================================
# 7. Utilities
# ==========================================
def generate_demo_dataset():
    print("\n[INFO] Generating Demo Dataset (5 Patients, 10 Visits, 20 Symptoms, 15 Medical Files, 5 AI Analyses, 5 Recommendations)...")
    session = get_session()
    now = get_utc_now()
    try:
        patients = []
        # 5 Patients
        for i in range(5):
            u = crud.create_user(
                session=session,
                user_id=uuid.uuid4(),
                email=f"demo_patient_{i}_{int(now.timestamp())}@example.com",
                password_hash="fake",
                role="patient",
                account_status="active",
                created_at=now,
                updated_at=now
            )
            patients.append(u)
            
        # 10 Visits
        visits = []
        for i in range(10):
            p = random.choice(patients)
            v = crud.create_visit(
                session=session,
                visit_id=uuid.uuid4(),
                user_id=p.user_id,
                visit_type="consultation",
                visit_reason=f"Routine checkup {i}",
                visit_date=now,
                status="completed",
                created_at=now,
                updated_at=now
            )
            visits.append(v)
            
        # 20 Symptoms (Requires Sessions)
        for i in range(20):
            p = random.choice(patients)
            # Just create a quick session for the symptom
            sess = crud.create_session(
                session=session,
                session_id=uuid.uuid4(),
                user_id=p.user_id,
                session_date=now,
                session_type="initial",
                status="completed",
                created_at=now,
                updated_at=now
            )
            crud.create_symptom(
                session=session,
                symptom_id=uuid.uuid4(),
                session_id=sess.session_id,
                user_id=p.user_id,
                symptom_name=f"Symptom {i}",
                severity=random.choice(["mild", "moderate", "severe"]),
                onset_date=now,
                created_at=now,
                updated_at=now
            )
            
        # 15 Medical Files (Mock metadata, no real upload to save space)
        for i in range(15):
            p = random.choice(patients)
            crud.create_medical_file(
                session=session,
                file_id=uuid.uuid4(),
                user_id=p.user_id,
                file_name=f"fake_mri_{i}.jpg",
                storage_path=f"fake/{p.user_id}/fake_mri_{i}.jpg",
                file_type="image/jpeg",
                mime_type="image/jpeg",
                file_size=1024,
                upload_date=now,
                analysis_status="pending",
                created_at=now,
                updated_at=now
            )
            
        # 5 Analyses & Recommendations
        for i in range(5):
            p = random.choice(patients)
            sess_id = session.query(SymptomSession).filter(SymptomSession.user_id == p.user_id).first()
            s_id = sess_id.session_id if sess_id else None
            
            analysis = crud.create_analysis(
                session=session,
                analysis_id=uuid.uuid4(),
                user_id=p.user_id,
                session_id=s_id,
                analysis_type="differential_diagnosis",
                findings=f"Findings {i}",
                confidence_score=0.9,
                risk_level="low",
                created_at=now,
                updated_at=now
            )
            
            crud.create_recommendation(
                session=session,
                recommendation_id=uuid.uuid4(),
                analysis_id=analysis.analysis_id,
                user_id=p.user_id,
                recommendation_type="specialist",
                title=f"Rec {i}",
                urgency="routine",
                status="pending",
                created_at=now,
                updated_at=now
            )
            
        print("✅ Demo Dataset Generated Successfully!")
    except Exception as e:
        print(f"❌ Error generating dataset: {e}")
    finally:
        session.close()

def utilities():
    while True:
        print_header("Utilities")
        print("1. Generate Demo Dataset")
        print("2. Database Statistics")
        print("3. Storage Statistics")
        print("4. Verify Connections")
        print("5. Back")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            generate_demo_dataset()
            pause()
            
        elif choice == '2':
            session = get_session()
            try:
                print("\n--- Database Statistics ---")
                print(f"Number of Users: {session.query(User).count()}")
                print(f"Number of Visits: {session.query(Visit).count()}")
                print(f"Number of Files: {session.query(MedicalFile).count()}")
                print(f"Number of Symptoms: {session.query(PatientSymptom).count()}")
                print(f"Number of Analyses: {session.query(AIAnalysis).count()}")
                print(f"Number of Recommendations: {session.query(Recommendation).count()}")
            finally:
                session.close()
            pause()
            
        elif choice == '3':
            print("\n--- Storage Statistics ---")
            print("To get precise storage size, consult the Supabase Dashboard.")
            session = get_session()
            try:
                files = session.query(MedicalFile).count()
                print(f"Total Uploaded Files (Metadata): {files}")
                print(f"Buckets Checked: medical_files")
            finally:
                session.close()
            pause()
            
        elif choice == '4':
            print("\n--- Connection Test ---")
            session = get_session()
            try:
                session.execute(text("SELECT 1"))
                print("✓ PostgreSQL: PASS")
                print("✓ SQLAlchemy Session: PASS")
            except Exception as e:
                print(f"❌ PostgreSQL: FAIL ({e})")
            finally:
                session.close()
                
            try:
                if supabase:
                    # quick bucket list check
                    supabase.storage.list_buckets()
                    print("✓ Supabase Storage: PASS")
                else:
                    print("❌ Supabase Storage: FAIL (Client not initialized)")
            except Exception as e:
                print(f"❌ Supabase Storage: FAIL ({e})")
            pause()
            
        elif choice == '5':
            break

# ==========================================
# Main execution
# ==========================================
def main_menu():
    while True:
        print_header("CarePath AI Developer CLI")
        print("1. Patient Management")
        print("2. Visit Management")
        print("3. Medical File Upload")
        print("4. Symptom Management")
        print("5. Medication Management")
        print("6. Database Viewer")
        print("7. Utilities")
        print("8. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            patient_management()
        elif choice == '2':
            visit_management()
        elif choice == '3':
            upload_medical_file()
        elif choice == '4':
            symptom_management()
        elif choice == '5':
            medication_management()
        elif choice == '6':
            database_viewer()
        elif choice == '7':
            utilities()
        elif choice == '8':
            clear_screen()
            print("Goodbye!\n")
            sys.exit(0)
        else:
            print("\nInvalid choice. Try again.")
            pause()

if __name__ == "__main__":
    main_menu()
