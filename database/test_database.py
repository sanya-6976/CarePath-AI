import os
import uuid
from datetime import datetime
from database.connections import SessionLocal, get_db
from database.crud import create_user, get_user, update_user, delete_user
from database.storage import upload_file, delete_file

def test_database_layer():
    print("Starting Database Layer Tests...\n")
    
    # 1. Test Session Creation
    if SessionLocal is None:
        print("[FAIL] SessionLocal is None. Check .env configuration.")
        return
        
    session = SessionLocal()
    print("[OK] Session created successfully.")
    
    # Generate temporary UUIDs
    test_user_id = uuid.uuid4()
    
    try:
        # 2. Test CRUD Insert (Create User)
        print("Testing CRUD Insert...")
        user = create_user(
            session=session, 
            user_id=test_user_id, 
            email="test_temp_user@example.com", 
            password_hash="fake_hash_for_testing",
            role="patient",
            account_status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        print(f"[OK] User inserted successfully with ID: {user.user_id}")
        
        # 3. Test CRUD Read (Get User)
        print("Testing CRUD Read...")
        retrieved_user = get_user(session, test_user_id)
        if retrieved_user and retrieved_user.email == "test_temp_user@example.com":
            print("[OK] User read successfully.")
        else:
            print("[FAIL] User read mismatch or not found.")
            
        # 4. Test CRUD Update
        print("Testing CRUD Update...")
        updated_user = update_user(session, test_user_id, role="admin")
        if updated_user and updated_user.role == "admin":
            print("[OK] User updated successfully.")
        else:
            print("[FAIL] User update failed.")
            
        # 5. Test Storage
        # Create a dummy file for storage upload
        print("Testing Storage Upload...")
        test_file_path = "test_upload.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a temporary test file.")
            
        storage_dest = f"test_folder/{test_user_id}.txt"
        
        try:
            upload_metadata = upload_file(test_file_path, storage_dest)
            print(f"[OK] Storage upload successful. Public URL: {upload_metadata.get('public_url')}")
            
            # Test Storage Delete
            delete_success = delete_file(storage_dest)
            if delete_success:
                print("[OK] Storage delete successful.")
            else:
                print("[WARN] Storage delete returned false, verify in dashboard.")
        except Exception as e:
            print(f"[WARN] Storage tests skipped or failed: {e}")
            print("   Ensure you have a bucket configured and Supabase auth keys set.")
        finally:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                
    except Exception as e:
        print(f"[FAIL] Exception occurred during testing: {e}")
    finally:
        # 6. Clean up database records
        print("\nCleaning up temporary database records...")
        deleted = delete_user(session, test_user_id)
        if deleted:
            print(f"[OK] Deleted temporary user {test_user_id}")
        else:
            print(f"[WARN] Failed to delete temporary user {test_user_id} (maybe it was never created).")
            
        session.close()
        print("\n[OK] Database Layer Tests Completed.")

if __name__ == "__main__":
    test_database_layer()
