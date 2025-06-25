import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import List, Dict
import io

class EWASService:
    def run_analysis(
        self,
        epigenome_data: bytes,
        phenotype_data: bytes,
        phenotype_column: str,
        covariates: List[str]
    ) -> List[Dict]:
        # Load data
        epigenome_df = pd.read_csv(io.BytesIO(epigenome_data), sep='\t', index_col=0)
        phenotype_df = pd.read_csv(io.BytesIO(phenotype_data), index_col=0)
        
        # Align samples
        common_samples = epigenome_df.columns.intersection(phenotype_df.index)
        epigenome_df = epigenome_df[common_samples]
        phenotype_df = phenotype_df.loc[common_samples]
        
        # Prepare phenotype and covariates
        y = phenotype_df[phenotype_column]
        X_covariates = phenotype_df[covariates] if covariates else pd.DataFrame(index=phenotype_df.index)
        
        results = []
        
        # Run analysis for each CpG
        for cpg_id in epigenome_df.index:
            try:
                # Get methylation values for this CpG
                methylation = epigenome_df.loc[cpg_id]
                
                # Prepare design matrix
                X = pd.concat([methylation, X_covariates], axis=1)
                X = sm.add_constant(X)
                
                # Remove samples with missing data
                complete_cases = ~(X.isna().any(axis=1) | y.isna())
                X_clean = X[complete_cases]
                y_clean = y[complete_cases]
                
                if len(X_clean) < 10:  # Skip if too few samples
                    continue
                
                # Fit linear model
                model = sm.OLS(y_clean, X_clean)
                fitted_model = model.fit()
                
                # Extract results for methylation coefficient (first non-constant term)
                beta = fitted_model.params.iloc[1]  # Methylation coefficient
                p_value = fitted_model.pvalues.iloc[1]
                
                # Parse chromosome and position from CpG ID (assuming format like "chr1:12345")
                if ':' in cpg_id:
                    chrom, pos = cpg_id.split(':')
                    position = int(pos)
                else:
                    chrom = "unknown"
                    position = 0
                
                results.append({
                    'cpg_id': cpg_id,
                    'chromosome': chrom,
                    'position': position,
                    'beta': float(beta),
                    'p_value': float(p_value)
                })
                
            except Exception as e:
                # Skip problematic CpGs
                continue
        
        # Apply FDR correction
        if results:
            p_values = [r['p_value'] for r in results]
            fdr_values = self._benjamini_hochberg_correction(p_values)
            
            for i, result in enumerate(results):
                result['fdr'] = fdr_values[i]
        
        return results
    
    def _benjamini_hochberg_correction(self, p_values: List[float]) -> List[float]:
        """Apply Benjamini-Hochberg FDR correction"""
        n = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p_values = np.array(p_values)[sorted_indices]
        
        # Calculate FDR
        fdr_values = np.zeros(n)
        for i in range(n-1, -1, -1):
            if i == n-1:
                fdr_values[i] = sorted_p_values[i]
            else:
                fdr_values[i] = min(sorted_p_values[i] * n / (i + 1), fdr_values[i + 1])
        
        # Restore original order
        original_order_fdr = np.zeros(n)
        original_order_fdr[sorted_indices] = fdr_values
        
        return original_order_fdr.tolist()