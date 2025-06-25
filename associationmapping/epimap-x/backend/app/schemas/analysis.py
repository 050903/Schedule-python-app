from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    epigenome_file_id: int
    phenotype_file_id: int
    phenotype_column: str
    covariates: List[str]
    model_type: str = "linear_regression"

class AdvancedAnalysisRequest(BaseModel):
    epigenome_file_id: int
    phenotype_file_id: int
    phenotype_column: str
    covariates: List[str]
    random_effects: Optional[List[str]] = None
    model_type: str = "mixed_model"
    correction_method: str = "fdr"

class AnalysisResponse(BaseModel):
    analysis_id: int
    status: str
    message: str

class AnalysisStatusResponse(BaseModel):
    analysis_id: int
    status: str
    progress: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class BatchAnalysisRequest(BaseModel):
    analyses: List[AnalysisRequest]
    batch_name: str