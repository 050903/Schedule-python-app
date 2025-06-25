from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from app.db.session import get_session
from app.db.models import AnalysisJob, AnalysisStatus
from app.schemas.analysis import BatchAnalysisRequest, AnalysisResponse
from app.tasks.ewas_tasks import run_ewas_analysis
import json

router = APIRouter()

@router.post("/batch", response_model=dict)
async def submit_batch_analysis(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Submit multiple EWAS analyses as a batch"""
    batch_ids = []
    
    for i, analysis_req in enumerate(request.analyses):
        analysis_job = AnalysisJob(
            name=f"{request.batch_name}_{i+1}_{analysis_req.phenotype_column}",
            epigenome_file_id=analysis_req.epigenome_file_id,
            phenotype_file_id=analysis_req.phenotype_file_id,
            phenotype_column=analysis_req.phenotype_column,
            covariates=json.dumps(analysis_req.covariates),
            model_type=analysis_req.model_type,
            owner_id=1
        )
        
        session.add(analysis_job)
        session.commit()
        session.refresh(analysis_job)
        
        batch_ids.append(analysis_job.id)
        
        # Queue analysis
        background_tasks.add_task(run_ewas_analysis, analysis_job.id)
    
    return {
        "batch_name": request.batch_name,
        "analysis_ids": batch_ids,
        "total_analyses": len(batch_ids),
        "message": f"Batch of {len(batch_ids)} analyses submitted"
    }

@router.get("/batch/{batch_name}/status")
async def get_batch_status(
    batch_name: str,
    session: Session = Depends(get_session)
):
    """Get status of all analyses in a batch"""
    from sqlmodel import select
    
    statement = select(AnalysisJob).where(AnalysisJob.name.like(f"{batch_name}_%"))
    batch_analyses = session.exec(statement).all()
    
    if not batch_analyses:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    status_summary = {
        "batch_name": batch_name,
        "total_analyses": len(batch_analyses),
        "completed": sum(1 for a in batch_analyses if a.status == AnalysisStatus.COMPLETED),
        "running": sum(1 for a in batch_analyses if a.status == AnalysisStatus.RUNNING),
        "pending": sum(1 for a in batch_analyses if a.status == AnalysisStatus.PENDING),
        "failed": sum(1 for a in batch_analyses if a.status == AnalysisStatus.FAILED),
        "analyses": [
            {
                "analysis_id": a.id,
                "name": a.name,
                "status": a.status,
                "progress": a.progress
            }
            for a in batch_analyses
        ]
    }
    
    return status_summary

@router.get("/compare/{analysis_id_1}/{analysis_id_2}")
async def compare_analyses(
    analysis_id_1: int,
    analysis_id_2: int,
    session: Session = Depends(get_session)
):
    """Compare results between two analyses"""
    from sqlmodel import select
    from app.db.models import AnalysisResult
    
    # Get results for both analyses
    results_1 = session.exec(
        select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id_1)
    ).all()
    
    results_2 = session.exec(
        select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id_2)
    ).all()
    
    if not results_1 or not results_2:
        raise HTTPException(status_code=404, detail="Results not found for comparison")
    
    # Create comparison data
    results_1_dict = {r.cpg_id: r for r in results_1}
    results_2_dict = {r.cpg_id: r for r in results_2}
    
    common_cpgs = set(results_1_dict.keys()) & set(results_2_dict.keys())
    
    comparison_data = []
    for cpg_id in common_cpgs:
        r1 = results_1_dict[cpg_id]
        r2 = results_2_dict[cpg_id]
        
        comparison_data.append({
            "cpg_id": cpg_id,
            "beta_1": r1.beta,
            "beta_2": r2.beta,
            "p_value_1": r1.p_value,
            "p_value_2": r2.p_value,
            "beta_diff": abs(r1.beta - r2.beta),
            "consistent_direction": (r1.beta > 0) == (r2.beta > 0)
        })
    
    # Calculate correlation
    import numpy as np
    betas_1 = [d["beta_1"] for d in comparison_data]
    betas_2 = [d["beta_2"] for d in comparison_data]
    
    correlation = np.corrcoef(betas_1, betas_2)[0, 1] if len(betas_1) > 1 else 0
    
    return {
        "analysis_1": analysis_id_1,
        "analysis_2": analysis_id_2,
        "common_cpgs": len(common_cpgs),
        "beta_correlation": float(correlation),
        "consistent_direction_pct": sum(d["consistent_direction"] for d in comparison_data) / len(comparison_data) * 100,
        "comparison_data": comparison_data[:100]  # Limit for response size
    }