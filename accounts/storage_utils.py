"""
Supabase Storage utility functions for file uploads
"""
 
from supabase import create_client, Client
from django.conf import settings
import uuid
import os
 
 
def get_supabase_client(use_service_key=False) -> Client:
    """Initialize Supabase client"""
    project_ref = "egllznsxjgkhnwexidii"
    url = f"https://{project_ref}.supabase.co"
   
    # Choose service key for backend uploads, anon key otherwise
    if use_service_key:
        key = os.environ.get('SUPABASE_KEY_SERVICE', settings.SUPABASE_KEY_SERVICE)
    else:
        key = os.environ.get('SUPABASE_KEY', settings.SUPABASE_KEY)
   
    return create_client(url, key)
 
 
 
def upload_to_supabase(file, bucket_name='user-uploads', folder=''):
    """
    Upload file to Supabase Storage
   
    Args:
        file: Django UploadedFile object
        bucket_name: Name of the Supabase storage bucket (default: 'user-uploads')
        folder: Optional folder path within the bucket (e.g., 'profile-photos')
   
    Returns:
        str: Public URL of the uploaded file, or None if upload fails
    """
    try:
        supabase = get_supabase_client()
        # Use service key to bypass RLS
        supabase = get_supabase_client(use_service_key=True)
        # Generate unique filename to prevent collisions
        ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
        unique_id = uuid.uuid4().hex
       
        # Construct the full path
        if folder:
            filename = f"{folder}/{unique_id}.{ext}"
        else:
            filename = f"{unique_id}.{ext}"
       
        # Read file content
        file.seek(0)  # Reset file pointer to beginning
        file_bytes = file.read()
       
        # Determine content type
        content_type = file.content_type if hasattr(file, 'content_type') else 'application/octet-stream'
       
        # Upload file to Supabase Storage
        response = supabase.storage.from_(bucket_name).upload(
            filename,
            file_bytes,
            file_options={"content-type": content_type}
        )
       
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
       
        return public_url
       
    except Exception as e:
        print(f"Error uploading to Supabase Storage: {e}")
        import traceback
        traceback.print_exc()
        return None
 
 
def delete_from_supabase(file_url, bucket_name='user-uploads'):
    """
    Delete file from Supabase Storage
   
    Args:
        file_url: Full public URL of the file to delete
        bucket_name: Name of the Supabase storage bucket
   
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        if not file_url:
            return False
           
        supabase = get_supabase_client()
       
        # Extract filename from URL
        # URL format: https://PROJECT_REF.supabase.co/storage/v1/object/public/BUCKET_NAME/FILENAME
        if '/object/public/' in file_url:
            parts = file_url.split('/object/public/')
            if len(parts) == 2:
                path_parts = parts[1].split('/', 1)
                if len(path_parts) == 2:
                    filename = path_parts[1]
                   
                    # Delete the file
                    supabase.storage.from_(bucket_name).remove([filename])
                    return True
       
        return False
       
    except Exception as e:
        print(f"Error deleting from Supabase Storage: {e}")
        return False