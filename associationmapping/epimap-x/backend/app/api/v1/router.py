from fastapi import APIRouter
from app.api.v1 import files, analysis, results, advanced_analysis, batch_analysis, multi_omics

api_router = APIRouter()

api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(results.router, prefix="/results", tags=["results"])
api_router.include_router(advanced_analysis.router, prefix="/advanced", tags=["advanced"])
api_router.include_router(batch_analysis.router, prefix="/batch", tags=["batch"])
api_router.include_router(multi_omics.router, prefix="/multi-omics", tags=["multi-omics"])