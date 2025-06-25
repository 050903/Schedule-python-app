from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.db.session import get_session
from app.db.models import DataFile, FileType
from app.services.file_storage_service import FileStorageService
from app.schemas.file import FileResponse

router = APIRouter()

@router.post("/upload/epigenome", response_model=FileResponse)
async def upload_epigenome_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if not file.filename.endswith(('.tsv', '.csv', '.bed')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    storage_service = FileStorageService()
    file_path = await storage_service.upload_file(file, FileType.EPIGENOME)
    
    db_file = DataFile(
        filename=file.filename,
        file_type=FileType.EPIGENOME,
        file_path=file_path,
        file_size=file.size or 0,
        owner_id=1  # TODO: Get from current user
    )
    
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    
    return FileResponse(
        file_id=db_file.id,
        filename=db_file.filename,
        status="uploaded"
    )

@router.post("/upload/phenotype", response_model=FileResponse)
async def upload_phenotype_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if not file.filename.endswith(('.csv', '.tsv')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    storage_service = FileStorageService()
    file_path = await storage_service.upload_file(file, FileType.PHENOTYPE)
    
    db_file = DataFile(
        filename=file.filename,
        file_type=FileType.PHENOTYPE,
        file_path=file_path,
        file_size=file.size or 0,
        owner_id=1  # TODO: Get from current user
    )
    
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    
    return FileResponse(
        file_id=db_file.id,
        filename=db_file.filename,
        status="uploaded"
    )

@router.get("/", response_model=List[dict])
async def list_files(session: Session = Depends(get_session)):
    files = session.query(DataFile).filter(DataFile.owner_id == 1).all()  # TODO: Filter by current user
    return [
        {
            "file_id": f.id,
            "filename": f.filename,
            "type": f.file_type,
            "size_bytes": f.file_size,
            "uploaded_at": f.uploaded_at
        }
        for f in files
    ]