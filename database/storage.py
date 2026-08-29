import os
import mimetypes
from typing import Dict, Any
from database.connections import supabase

BUCKET_NAME = os.getenv("STORAGE_BUCKET_NAME", "medical_files")

def upload_file(file_path: str, destination_path: str) -> Dict[str, Any]:
    """
    Uploads a local file to Supabase Storage.
    
    Args:
        file_path (str): Local path to the file to upload.
        destination_path (str): Path in the Supabase Storage bucket.
        
    Returns:
        Dict[str, Any]: Metadata about the uploaded file.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized. Check .env configuration.")
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as f:
        res = supabase.storage.from_(BUCKET_NAME).upload(
            path=destination_path,
            file=f,
            file_options={"content-type": mime_type}
        )
    
    # Get public URL (Assuming bucket is public, otherwise use signed URL)
    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(destination_path)

    return {
        "storage_path": destination_path,
        "public_url": public_url,
        "file_name": file_name,
        "mime_type": mime_type,
        "file_size": file_size
    }

def download_file(storage_path: str, local_destination: str) -> str:
    """
    Downloads a file from Supabase Storage.
    
    Args:
        storage_path (str): Path of the file in the Supabase bucket.
        local_destination (str): Local path to save the downloaded file.
        
    Returns:
        str: The local_destination path.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized.")
        
    res = supabase.storage.from_(BUCKET_NAME).download(storage_path)
    with open(local_destination, "wb") as f:
        f.write(res)
    return local_destination

def delete_file(storage_path: str) -> bool:
    """
    Deletes a file from Supabase Storage.
    
    Args:
        storage_path (str): Path of the file in the Supabase bucket.
        
    Returns:
        bool: True if deleted successfully.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized.")
        
    # remove takes a list of paths
    res = supabase.storage.from_(BUCKET_NAME).remove([storage_path])
    return True if res else False

def get_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """
    Generates a signed URL for temporary access to a private file.
    
    Args:
        storage_path (str): Path of the file in the Supabase bucket.
        expires_in (int): Number of seconds until the URL expires.
        
    Returns:
        str: The signed URL.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized.")
        
    res = supabase.storage.from_(BUCKET_NAME).create_signed_url(storage_path, expires_in)
    return res.get('signedURL', '') if isinstance(res, dict) else res
