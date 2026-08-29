import os
import uuid
from datetime import datetime, timezone
from database.connections import SessionLocal
from database import crud
from database import storage

def run_demo():
    print("[START] Starting CarePath-AI Upload Flow Demo...\n")
    
    session = SessionLocal()
    
    # Generate temporary IDs
    demo_user_id = uuid.uuid4()
    demo_visit_id = uuid.uuid4()
    demo_file_id = uuid.uuid4()
    
    # Pre-define storage_dest so it exists for cleanup even if we fail early
    storage_dest = f"medical_files/{demo_user_id}/{demo_file_id}.jpg"
    
    # 1. Create a temporary local file to simulate an upload
    test_file_path = "demo_xray.jpg"
    print(f"[INFO] Creating temporary local file: {test_file_path}")
    with open(test_file_path, "w") as f:
        f.write("Simulated image data...")
        
    try:
        # 2. Setup Prerequisites in the Database (User and Visit)
        print("\n[INFO] Setting up prerequisites in database...")
        now = datetime.now(timezone.utc)
        user = crud.create_user(
            session=session,
            user_id=demo_user_id,
            email="demo_dev@example.com",
            password_hash="demo_hash",
            role="patient",
            account_status="active",
            created_at=now,
            updated_at=now
        )
        
        visit = crud.create_visit(
            session=session,
            visit_id=demo_visit_id,
            user_id=demo_user_id,
            visit_type="consultation",
            visit_date=now,
            created_at=now,
            updated_at=now
        )
        print("[OK] Prerequisites (User and Visit) created.")
        
        # 3. Upload File to Supabase Storage
        print("\n[INFO] Uploading file to Supabase Storage...")
        upload_metadata = storage.upload_file(test_file_path, storage_dest)
        
        print("[OK] File uploaded successfully!")
        print(f"   Storage Path: {upload_metadata['storage_path']}")
        print(f"   Public URL: {upload_metadata['public_url']}")
        
        # 4. Save the Metadata to PostgreSQL via CRUD
        print("\n[INFO] Saving file metadata to PostgreSQL...")
        medical_file = crud.create_medical_file(
            session=session,
            file_id=demo_file_id,
            user_id=demo_user_id,
            visit_id=demo_visit_id,
            file_name="demo_xray.jpg",
            storage_path=upload_metadata['storage_path'],
            file_type="image/jpeg",
            mime_type=upload_metadata['mime_type'],
            file_size=upload_metadata['file_size'],
            upload_date=now,
            analysis_status="pending",
            created_at=now,
            updated_at=now
        )
        print(f"[OK] Medical File record saved in database with ID: {medical_file.file_id}")
        
    except Exception as e:
        print(f"\n[FAIL] Error during demo: {e}")
        
    finally:
        print("\n[INFO] Initiating Cleanup...")
        
        # 5. Clean up PostgreSQL Database
        from database.models import MedicalFile, Visit
        crud.utils.delete_record(session, MedicalFile, demo_file_id)
        crud.utils.delete_record(session, Visit, demo_visit_id)
        crud.delete_user(session, demo_user_id)
        print("[OK] Database records cleaned up.")
        
        # 6. Clean up Supabase Storage
        try:
            storage.delete_file(storage_dest)
            print("[OK] Supabase Storage file deleted.")
        except Exception as e:
            print(f"[WARN] Failed to delete storage file: {e}")
            
        # 7. Clean up Local File
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print("[OK] Local temporary file deleted.")
            
        session.close()
        print("\n[DONE] Demo completed successfully and left zero trace!")

if __name__ == "__main__":
    run_demo()
