from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    EPIGENOME = "epigenome"
    PHENOTYPE = "phenotype"
    EXPRESSION = "expression"
    GENOTYPE = "genotype"

class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DataFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    file_path: str
    size_bytes: int
    type: FileType
    owner_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    analyses_as_epigenome: List["AnalysisJob"] = Relationship(
        back_populates="epigenome_file",
        sa_relationship_kwargs={"foreign_keys": "AnalysisJob.epigenome_file_id"}
    )
    analyses_as_phenotype: List["AnalysisJob"] = Relationship(
        back_populates="phenotype_file",
        sa_relationship_kwargs={"foreign_keys": "AnalysisJob.phenotype_file_id"}
    )

class AnalysisJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    epigenome_file_id: int = Field(foreign_key="datafile.id")
    phenotype_file_id: int = Field(foreign_key="datafile.id")
    phenotype_column: str
    covariates: str  # JSON string
    model_type: str
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    progress: int = Field(default=0)
    owner_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Relationships
    epigenome_file: Optional[DataFile] = Relationship(
        back_populates="analyses_as_epigenome",
        sa_relationship_kwargs={"foreign_keys": "AnalysisJob.epigenome_file_id"}
    )
    phenotype_file: Optional[DataFile] = Relationship(
        back_populates="analyses_as_phenotype", 
        sa_relationship_kwargs={"foreign_keys": "AnalysisJob.phenotype_file_id"}
    )
    results: List["AnalysisResult"] = Relationship(back_populates="analysis")

class AnalysisResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cpg_id: str
    chromosome: str
    position: int
    beta: float
    se: Optional[float] = None
    p_value: float
    fdr: Optional[float] = None
    bonferroni: Optional[float] = None
    analysis_id: int = Field(foreign_key="analysisjob.id")
    
    # Relationships
    analysis: Optional[AnalysisJob] = Relationship(back_populates="results")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MLModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    model_type: str  # classification, regression
    file_path: str  # Path to saved model
    performance_metrics: str  # JSON string
    feature_count: int
    analysis_id: int = Field(foreign_key="analysisjob.id")
    owner_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cpg_id: str = Field(unique=True)
    gene_symbol: Optional[str] = None
    gene_id: Optional[str] = None
    chromosome: str
    position: int
    feature_type: str  # gene_body, promoter, enhancer, etc.
    cpg_island_status: str  # island, shore, shelf, open_sea
    created_at: datetime = Field(default_factory=datetime.utcnow)