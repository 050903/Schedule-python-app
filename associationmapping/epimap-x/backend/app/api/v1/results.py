from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import AnalysisResult, AnalysisJob
from typing import List
import numpy as np

router = APIRouter()

@router.get("/{analysis_id}/manhattan")
async def get_manhattan_data(
    analysis_id: int,
    session: Session = Depends(get_session)
):
    # Verify analysis exists
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get results
    statement = select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)
    results = session.exec(statement).all()
    
    manhattan_data = []
    for result in results:
        log10_p = -np.log10(max(result.p_value, 1e-300))  # Avoid log(0)
        manhattan_data.append({
            "chrom": result.chromosome,
            "pos": result.position,
            "p_value": result.p_value,
            "log10_p": log10_p,
            "cpg_id": result.cpg_id
        })
    
    return manhattan_data

@router.get("/{analysis_id}/qqplot_data")
async def get_qqplot_data(
    analysis_id: int,
    session: Session = Depends(get_session)
):
    # Verify analysis exists
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get p-values
    statement = select(AnalysisResult.p_value).where(AnalysisResult.analysis_id == analysis_id)
    p_values = session.exec(statement).all()
    
    if not p_values:
        return []
    
    # Calculate expected vs observed
    p_values = np.array(p_values)
    p_values = p_values[~np.isnan(p_values)]  # Remove NaN values
    p_values = np.sort(p_values)
    
    n = len(p_values)
    expected = np.arange(1, n + 1) / (n + 1)
    
    qq_data = []
    for i in range(n):
        qq_data.append({
            "expected": -np.log10(expected[i]),
            "observed": -np.log10(max(p_values[i], 1e-300))
        })
    
    return qq_data

@router.get("/{analysis_id}/table")
async def get_results_table(
    analysis_id: int,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    # Verify analysis exists
    analysis = session.get(AnalysisJob, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get results with pagination, ordered by p-value
    statement = (
        select(AnalysisResult)
        .where(AnalysisResult.analysis_id == analysis_id)
        .order_by(AnalysisResult.p_value)
        .offset(offset)
        .limit(limit)
    )
    results = session.exec(statement).all()
    
    table_data = []
    for result in results:
        table_data.append({
            "cpg_id": result.cpg_id,
            "chromosome": result.chromosome,
            "position": result.position,
            "beta": result.beta,
            "p_value": result.p_value,
            "fdr": result.fdr
        })
    
    return table_data