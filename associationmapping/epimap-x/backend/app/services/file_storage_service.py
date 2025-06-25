from fastapi import UploadFile
from app.core.config import settings
from app.db.models import FileType
import uuid
import os
import shutil

class FileStorageService:
    def __init__(self):
        # Create local storage directory if it doesn't exist
        os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    
    async def upload_file(self, file: UploadFile, file_type: FileType) -> str:
        file_id = str(uuid.uuid4())
        file_path = f"{file_type.value}/{file_id}_{file.filename}"
        full_path = os.path.join(settings.LOCAL_STORAGE_PATH, file_path)
        
        # Create subdirectory
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Save file
        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path
    
    def download_file(self, file_path: str) -> bytes:
        full_path = os.path.join(settings.LOCAL_STORAGE_PATH, file_path)
        with open(full_path, "rb") as f:
            return f.read()