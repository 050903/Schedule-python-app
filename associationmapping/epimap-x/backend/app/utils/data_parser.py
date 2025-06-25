import pandas as pd
import numpy as np
from typing import Tuple, List
import io

class DataParser:
    @staticmethod
    def parse_epigenome_file(file_data: bytes, file_format: str = "tsv") -> pd.DataFrame:
        """Parse epigenome data file (TSV/CSV format)"""
        if file_format.lower() == "tsv":
            df = pd.read_csv(io.BytesIO(file_data), sep='\t', index_col=0)
        else:
            df = pd.read_csv(io.BytesIO(file_data), index_col=0)
        
        # Validate data format
        if df.empty:
            raise ValueError("Empty epigenome data file")
        
        # Check for numeric values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            raise ValueError("No numeric methylation values found")
        
        return df
    
    @staticmethod
    def parse_phenotype_file(file_data: bytes, file_format: str = "csv") -> pd.DataFrame:
        """Parse phenotype data file (CSV/TSV format)"""
        if file_format.lower() == "tsv":
            df = pd.read_csv(io.BytesIO(file_data), sep='\t', index_col=0)
        else:
            df = pd.read_csv(io.BytesIO(file_data), index_col=0)
        
        # Validate data format
        if df.empty:
            raise ValueError("Empty phenotype data file")
        
        return df
    
    @staticmethod
    def validate_sample_overlap(epigenome_df: pd.DataFrame, phenotype_df: pd.DataFrame) -> Tuple[List[str], int]:
        """Validate sample overlap between epigenome and phenotype data"""
        epigenome_samples = set(epigenome_df.columns)
        phenotype_samples = set(phenotype_df.index)
        
        common_samples = epigenome_samples.intersection(phenotype_samples)
        
        if len(common_samples) < 10:
            raise ValueError(f"Insufficient sample overlap: {len(common_samples)} samples")
        
        return list(common_samples), len(common_samples)