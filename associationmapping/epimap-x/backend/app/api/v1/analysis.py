from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from app.db.session import get_session
from app.db.models import AnalysisJob, AnalysisStatus
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisStatusResponse
from app.tasks.ewas_tasks import run_ewas_analysis
import json

router = APIRouter()

@router.post("/ewas", response_model=AnalysisResponse)
async def create_ewas_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    analysis_job = AnalysisJob(
        name=f"EWAS_{request.phenotype_column}",
        epigenome_file_id=request.epigenome_file_id,
        phenotype_file_id=request.phenotype_file_id,
        phenotype_column=request.phenotype_column,
        covariates=json.dumps(request.covariates),
        model_type=request.model_type,
        owner_id=1  # TODO: Get from current user
    )
    
    session.add(analysis_job)
    session.commit()
    session.refresh(analysis_job)
    
    # Run analysis in background
    background_tasks.add_task(run_ewas_analysis, analysis_job.id)
    
    return AnalysisResponse(
        analysis_id=analysis_job.id,
        status=analysis_job.status,
        message="Analysis job submitted."
    )

@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    analysis_id: int,
    session: Session = Depends(get_session)
):
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AnalysisStatusResponse(
        analysis_id=analysis.id,
        status=analysis.status,
        progress=analysis.progress,
        start_time=analysis.started_at,
        end_time=analysis.completed_at,
        error_message=analysis.error_message
    )

@router.get("/all")
async def list_analyses(session: Session = Depends(get_session)):
    analyses = session.query(AnalysisJob).filter(AnalysisJob.owner_id == 1).all()
    return [
        {
            "analysis_id": a.id,
            "name": a.name,
            "status": a.status,
            "submitted_at": a.created_at
        }
        for a in analyses
    ]