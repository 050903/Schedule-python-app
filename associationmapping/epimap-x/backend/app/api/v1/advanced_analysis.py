from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from app.db.session import get_session
from app.db.models import AnalysisJob, AnalysisStatus
from app.schemas.analysis import AdvancedAnalysisRequest, AnalysisResponse
from app.services.advanced_ewas_service import AdvancedEWASService
from app.services.annotation_service import AnnotationService
import json

router = APIRouter()

@router.post("/ewas-advanced", response_model=AnalysisResponse)
async def create_advanced_ewas_analysis(
    request: AdvancedAnalysisRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Submit advanced EWAS analysis with mixed models"""
    analysis_job = AnalysisJob(
        name=f"Advanced_EWAS_{request.phenotype_column}",
        epigenome_file_id=request.epigenome_file_id,
        phenotype_file_id=request.phenotype_file_id,
        phenotype_column=request.phenotype_column,
        covariates=json.dumps(request.covariates),
        model_type="mixed_model",
        owner_id=1
    )
    
    session.add(analysis_job)
    session.commit()
    session.refresh(analysis_job)
    
    # Run advanced analysis in background
    background_tasks.add_task(run_advanced_ewas_analysis, analysis_job.id, request.random_effects)
    
    return AnalysisResponse(
        analysis_id=analysis_job.id,
        status=analysis_job.status,
        message="Advanced EWAS analysis submitted."
    )

@router.post("/annotate/{analysis_id}")
async def annotate_results(
    analysis_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Annotate analysis results with gene information"""
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    background_tasks.add_task(annotate_analysis_results, analysis_id)
    
    return {"message": "Annotation started", "analysis_id": analysis_id}

@router.get("/pathway-enrichment/{analysis_id}")
async def get_pathway_enrichment(
    analysis_id: int,
    p_threshold: float = 0.05,
    session: Session = Depends(get_session)
):
    """Get pathway enrichment for significant CpGs"""
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get significant results
    from sqlmodel import select
    from app.db.models import AnalysisResult
    
    statement = (
        select(AnalysisResult)
        .where(AnalysisResult.analysis_id == analysis_id)
        .where(AnalysisResult.p_value < p_threshold)
    )
    significant_results = session.exec(statement).all()
    
    if not significant_results:
        return {"pathways": {}, "message": "No significant results found"}
    
    # Mock gene extraction (would need annotation data)
    genes = [f"GENE_{i}" for i in range(len(significant_results))]
    
    annotation_service = AnnotationService()
    pathways = annotation_service.get_pathway_enrichment(genes)
    
    return {"pathways": pathways, "gene_count": len(genes)}

async def run_advanced_ewas_analysis(analysis_id: int, random_effects: list = None):
    """Run advanced EWAS analysis with mixed models"""
    from sqlmodel import create_engine
    from app.core.config import settings
    from app.db.models import DataFile, AnalysisResult
    from app.services.file_storage_service import FileStorageService
    from datetime import datetime
    
    engine = create_engine(settings.DATABASE_URL)
    
    with Session(engine) as session:
        try:
            analysis = session.get(AnalysisJob, analysis_id)
            if not analysis:
                return
            
            # Update status
            analysis.status = AnalysisStatus.RUNNING
            analysis.started_at = datetime.utcnow()
            analysis.progress = 10
            session.commit()
            
            # Get files
            epigenome_file = session.get(DataFile, analysis.epigenome_file_id)
            phenotype_file = session.get(DataFile, analysis.phenotype_file_id)
            
            if not epigenome_file or not phenotype_file:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = "Required files not found"
                session.commit()
                return
            
            # Load data
            storage_service = FileStorageService()
            epigenome_data = storage_service.download_file(epigenome_file.file_path)
            phenotype_data = storage_service.download_file(phenotype_file.file_path)
            
            analysis.progress = 30
            session.commit()
            
            # Run advanced analysis
            ewas_service = AdvancedEWASService()
            covariates = json.loads(analysis.covariates)
            
            results = ewas_service.run_mixed_model_analysis(
                epigenome_data=epigenome_data,
                phenotype_data=phenotype_data,
                phenotype_column=analysis.phenotype_column,
                covariates=covariates,
                random_effects=random_effects
            )
            
            analysis.progress = 80
            session.commit()
            
            # Save results
            for result in results:
                db_result = AnalysisResult(
                    cpg_id=result['cpg_id'],
                    chromosome=result['chromosome'],
                    position=result['position'],
                    beta=result['beta'],
                    p_value=result['p_value'],
                    fdr=result.get('fdr'),
                    analysis_id=analysis_id
                )
                session.add(db_result)
            
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress = 100
            session.commit()
            
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            session.commit()

async def annotate_analysis_results(analysis_id: int):
    """Annotate analysis results with gene information"""
    # This would run annotation in background
    pass