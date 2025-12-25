import os
import uuid
from pathlib import Path

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from ..config import settings

# Local storage directory - relative to the project root
LOCAL_STORAGE_DIR = Path(__file__).parent.parent.parent / "CV_documents"

class StorageService:
    def __init__(self):
        self.use_local = True  # Default to local storage
        self.client = None
        self.bucket = None
        
        # Try to initialize Supabase if configured
        if SUPABASE_AVAILABLE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                self.bucket = settings.SUPABASE_BUCKET
                self.use_local = False
                print("StorageService: Using Supabase storage")
            except Exception as e:
                print(f"StorageService: Supabase init failed ({e}), using local storage")
                self.use_local = True
        else:
            print("StorageService: Supabase not configured, using local storage")
        
        # Ensure local directory exists
        LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    def upload_resume(self, file_content: bytes, original_filename: str) -> str:
        """Upload resume to storage and return URL/path."""
        # Generate unique filename
        file_ext = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        if self.use_local:
            return self._upload_local(file_content, unique_filename)
        else:
            return self._upload_supabase(file_content, unique_filename)
    
    def _upload_local(self, file_content: bytes, filename: str) -> str:
        """Upload to local file system."""
        file_path = LOCAL_STORAGE_DIR / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Return a URL path that the backend can serve
        return f"/files/resumes/{filename}"
    
    def _upload_supabase(self, file_content: bytes, filename: str) -> str:
        """Upload to Supabase storage."""
        # Upload file
        response = self.client.storage.from_(self.bucket).upload(
            path=filename,
            file=file_content,
            file_options={"content-type": "application/pdf"}
        )
        
        # Get public URL
        public_url = self.client.storage.from_(self.bucket).get_public_url(filename)
        
        return public_url
    
    def delete_resume(self, file_url: str) -> bool:
        """Delete resume from storage."""
        # Extract filename from URL
        filename = file_url.split('/')[-1]
        
        if self.use_local:
            return self._delete_local(filename)
        else:
            return self._delete_supabase(filename)
    
    def _delete_local(self, filename: str) -> bool:
        """Delete from local file system."""
        try:
            file_path = LOCAL_STORAGE_DIR / filename
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception:
            return False
    
    def _delete_supabase(self, filename: str) -> bool:
        """Delete from Supabase storage."""
        try:
            self.client.storage.from_(self.bucket).remove([filename])
            return True
        except Exception:
            return False
    
    def get_local_file_path(self, filename: str) -> Path:
        """Get the local file path for a filename."""
        return LOCAL_STORAGE_DIR / filename

storage_service = StorageService()
