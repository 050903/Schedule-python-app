from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlmodel import Session
from app.db.session import get_session
from app.db.models import AnalysisJob, AnalysisStatus, DataFile, FileType
from app.services.multi_omics_service import MultiOmicsService
from app.services.machine_learning_service import MachineLearningService
from app.services.file_storage_service import FileStorageService
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter()

class MultiOmicsRequest(BaseModel):
    methylation_file_id: int
    expression_file_id: int
    phenotype_file_id: int
    phenotype_column: str
    analysis_type: str = "integration"

class MLRequest(BaseModel):
    methylation_file_id: int
    phenotype_file_id: int
    phenotype_column: str
    model_type: str = "classification"

@router.post("/upload/expression")
async def upload_expression_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload gene expression data file"""
    storage_service = FileStorageService()
    
    try:
        file_path = await storage_service.upload_file(file, FileType.EXPRESSION)
        
        db_file = DataFile(
            filename=file.filename,
            file_path=file_path,
            size_bytes=file.size,
            type=FileType.EXPRESSION,
            owner_id=1
        )
        
        session.add(db_file)
        session.commit()
        session.refresh(db_file)
        
        return {
            "file_id": db_file.id,
            "filename": db_file.filename,
            "message": "Expression file uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integration")
async def run_multi_omics_integration(
    request: MultiOmicsRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Run multi-omics integration analysis"""
    
    # Create analysis job
    analysis_job = AnalysisJob(
        name=f"MultiOmics_{request.phenotype_column}",
        epigenome_file_id=request.methylation_file_id,
        phenotype_file_id=request.phenotype_file_id,
        phenotype_column=request.phenotype_column,
        covariates=json.dumps([]),
        model_type="multi_omics",
        owner_id=1
    )
    
    session.add(analysis_job)
    session.commit()
    session.refresh(analysis_job)
    
    # Run integration in background
    background_tasks.add_task(
        run_integration_analysis, 
        analysis_job.id, 
        request.expression_file_id
    )
    
    return {
        "analysis_id": analysis_job.id,
        "status": "submitted",
        "message": "Multi-omics integration analysis started"
    }

@router.post("/ml-training")
async def train_ml_model(
    request: MLRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Train machine learning model for phenotype prediction"""
    
    # Create analysis job
    analysis_job = AnalysisJob(
        name=f"ML_{request.model_type}_{request.phenotype_column}",
        epigenome_file_id=request.methylation_file_id,
        phenotype_file_id=request.phenotype_file_id,
        phenotype_column=request.phenotype_column,
        covariates=json.dumps([]),
        model_type=f"ml_{request.model_type}",
        owner_id=1
    )
    
    session.add(analysis_job)
    session.commit()
    session.refresh(analysis_job)
    
    # Train model in background
    background_tasks.add_task(
        train_ml_model_task,
        analysis_job.id,
        request.model_type
    )
    
    return {
        "analysis_id": analysis_job.id,
        "status": "submitted",
        "message": f"ML {request.model_type} training started"
    }

@router.get("/integration/{analysis_id}/results")
async def get_integration_results(
    analysis_id: int,
    session: Session = Depends(get_session)
):
    """Get multi-omics integration results"""
    
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != AnalysisStatus.COMPLETED:
        return {"status": analysis.status, "message": "Analysis not completed"}
    
    # Load results from file or database
    # For now, return mock results
    return {
        "analysis_id": analysis_id,
        "integration_type": "methylation_expression",
        "sample_count": 100,
        "significant_correlations": 25,
        "top_correlations": [
            {"methylation_id": "chr1:12345", "expression_id": "GENE1", "correlation": 0.85},
            {"methylation_id": "chr2:67890", "expression_id": "GENE2", "correlation": -0.78}
        ],
        "pca_variance_explained": [0.35, 0.22, 0.15, 0.12, 0.08]
    }

@router.get("/ml-model/{analysis_id}/performance")
async def get_ml_model_performance(
    analysis_id: int,
    session: Session = Depends(get_session)
):
    """Get ML model performance metrics"""
    
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != AnalysisStatus.COMPLETED:
        return {"status": analysis.status, "message": "Model training not completed"}
    
    # Return mock performance metrics
    if "classification" in analysis.model_type:
        return {
            "model_type": "classification",
            "accuracy": 0.85,
            "auc": 0.92,
            "cv_mean": 0.83,
            "cv_std": 0.05,
            "feature_count": 1000,
            "top_features": [
                {"feature": "chr1:12345", "importance": 0.15},
                {"feature": "chr2:67890", "importance": 0.12}
            ]
        }
    else:
        return {
            "model_type": "regression",
            "r2": 0.78,
            "rmse": 0.45,
            "cv_mean": 0.75,
            "cv_std": 0.08,
            "feature_count": 1000,
            "top_features": [
                {"feature": "chr3:11111", "importance": 0.18},
                {"feature": "chr4:22222", "importance": 0.14}
            ]
        }

@router.post("/ml-predict/{analysis_id}")
async def predict_with_model(
    analysis_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Make predictions using trained ML model"""
    
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Model not ready")
    
    # For now, return mock predictions
    return {
        "model_id": f"model_{analysis_id}",
        "predictions": [0, 1, 1, 0, 1],
        "sample_ids": ["Sample1", "Sample2", "Sample3", "Sample4", "Sample5"],
        "confidence_scores": [0.85, 0.92, 0.78, 0.88, 0.95]
    }

async def run_integration_analysis(analysis_id: int, expression_file_id: int):
    """Background task for multi-omics integration"""
    from sqlmodel import create_engine
    from app.core.config import settings
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
            analysis.progress = 20
            session.commit()
            
            # Get files
            meth_file = session.get(DataFile, analysis.epigenome_file_id)
            expr_file = session.get(DataFile, expression_file_id)
            pheno_file = session.get(DataFile, analysis.phenotype_file_id)
            
            if not all([meth_file, expr_file, pheno_file]):
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = "Required files not found"
                session.commit()
                return
            
            analysis.progress = 50
            session.commit()
            
            # Run integration (mock for now)
            # multi_omics_service = MultiOmicsService()
            # results = multi_omics_service.integrate_methylation_expression(...)
            
            analysis.progress = 90
            session.commit()
            
            # Complete
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress = 100
            session.commit()
            
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            session.commit()

async def train_ml_model_task(analysis_id: int, model_type: str):
    """Background task for ML model training"""
    from sqlmodel import create_engine
    from app.core.config import settings
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
            analysis.progress = 20
            session.commit()
            
            # Mock training process
            analysis.progress = 60
            session.commit()
            
            # Complete
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress = 100
            session.commit()
            
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            session.commit()