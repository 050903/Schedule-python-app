from pydantic import BaseModel
from typing import Optional

class FileResponse(BaseModel):
    file_id: int
    filename: str
    status: str

class FileUpload(BaseModel):
    filename: str
    file_type: str