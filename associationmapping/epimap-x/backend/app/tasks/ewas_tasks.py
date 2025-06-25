from sqlmodel import Session, create_engine
from app.core.config import settings
from app.db.models import AnalysisJob, AnalysisResult, DataFile, AnalysisStatus
from app.services.file_storage_service import FileStorageService
from app.services.ewas_service import EWASService
import json
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)

def run_ewas_analysis(analysis_id: int):
    """Run EWAS analysis synchronously (without Celery for now)"""
    with Session(engine) as session:
        try:
            # Get analysis job
            analysis = session.get(AnalysisJob, analysis_id)
            if not analysis:
                return {"error": "Analysis job not found"}
            
            # Update status to RUNNING
            analysis.status = AnalysisStatus.RUNNING
            analysis.started_at = datetime.utcnow()
            analysis.progress = 10
            session.commit()
            
            # Get file information
            epigenome_file = session.get(DataFile, analysis.epigenome_file_id)
            phenotype_file = session.get(DataFile, analysis.phenotype_file_id)
            
            if not epigenome_file or not phenotype_file:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = "Required files not found"
                session.commit()
                return {"error": "Required files not found"}
            
            # Download files from storage
            storage_service = FileStorageService()
            epigenome_data = storage_service.download_file(epigenome_file.file_path)
            phenotype_data = storage_service.download_file(phenotype_file.file_path)
            
            analysis.progress = 30
            session.commit()
            
            # Run EWAS analysis
            ewas_service = EWASService()
            covariates = json.loads(analysis.covariates)
            
            results = ewas_service.run_analysis(
                epigenome_data=epigenome_data,
                phenotype_data=phenotype_data,
                phenotype_column=analysis.phenotype_column,
                covariates=covariates
            )
            
            analysis.progress = 80
            session.commit()
            
            # Save results to database
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
            
            # Update analysis status
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.progress = 100
            session.commit()
            
            return {"status": "completed", "results_count": len(results)}
            
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            session.commit()
            return {"error": str(e)}