from supabase import create_client, Client
from ..config import settings
import uuid

class StorageService:
    def __init__(self):
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self.bucket = settings.SUPABASE_BUCKET
        else:
            self.client = None
            self.bucket = None
    
    def upload_resume(self, file_content: bytes, original_filename: str) -> str:
        """Upload resume to Supabase storage and return public URL."""
        if not self.client:
            raise Exception("Supabase not configured")
        
        # Generate unique filename
        file_ext = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Upload file
        response = self.client.storage.from_(self.bucket).upload(
            path=unique_filename,
            file=file_content,
            file_options={"content-type": "application/pdf"}
        )
        
        # Get public URL
        public_url = self.client.storage.from_(self.bucket).get_public_url(unique_filename)
        
        return public_url
    
    def delete_resume(self, file_url: str) -> bool:
        """Delete resume from Supabase storage."""
        if not self.client:
            return False
        
        # Extract filename from URL
        filename = file_url.split('/')[-1]
        
        try:
            self.client.storage.from_(self.bucket).remove([filename])
            return True
        except:
            return False

storage_service = StorageService()
