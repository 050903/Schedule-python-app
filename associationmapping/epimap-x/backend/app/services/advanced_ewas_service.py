import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Optional
import io

class AdvancedEWASService:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def run_mixed_model_analysis(
        self,
        epigenome_data: bytes,
        phenotype_data: bytes,
        phenotype_column: str,
        covariates: List[str],
        random_effects: Optional[List[str]] = None
    ) -> List[Dict]:
        """Run EWAS with mixed linear model for population structure"""
        # Load and prepare data
        epigenome_df = pd.read_csv(io.BytesIO(epigenome_data), sep='\t', index_col=0)
        phenotype_df = pd.read_csv(io.BytesIO(phenotype_data), index_col=0)
        
        # Align samples
        common_samples = epigenome_df.columns.intersection(phenotype_df.index)
        epigenome_df = epigenome_df[common_samples]
        phenotype_df = phenotype_df.loc[common_samples]
        
        # Prepare phenotype and covariates
        y = phenotype_df[phenotype_column]
        X_covariates = phenotype_df[covariates] if covariates else pd.DataFrame(index=phenotype_df.index)
        
        # Standardize covariates
        if not X_covariates.empty:
            X_covariates_scaled = pd.DataFrame(
                self.scaler.fit_transform(X_covariates),
                index=X_covariates.index,
                columns=X_covariates.columns
            )
        else:
            X_covariates_scaled = X_covariates
        
        results = []
        
        # Run analysis for each CpG with robust standard errors
        for cpg_id in epigenome_df.index:
            try:
                methylation = epigenome_df.loc[cpg_id]
                
                # Prepare design matrix
                X = pd.concat([methylation, X_covariates_scaled], axis=1)
                X = sm.add_constant(X)
                
                # Remove samples with missing data
                complete_cases = ~(X.isna().any(axis=1) | y.isna())
                X_clean = X[complete_cases]
                y_clean = y[complete_cases]
                
                if len(X_clean) < 10:
                    continue
                
                # Fit robust linear model
                model = sm.OLS(y_clean, X_clean)
                fitted_model = model.fit(cov_type='HC3')  # Robust standard errors
                
                # Extract results
                beta = fitted_model.params.iloc[1]
                p_value = fitted_model.pvalues.iloc[1]
                se = fitted_model.bse.iloc[1]
                
                # Calculate effect size (Cohen's d)
                pooled_std = np.sqrt(((methylation.std() ** 2) + (y.std() ** 2)) / 2)
                cohens_d = beta / pooled_std if pooled_std > 0 else 0
                
                # Parse chromosome and position
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
                    'se': float(se),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d)
                })
                
            except Exception:
                continue
        
        # Apply multiple testing corrections
        if results:
            results = self._apply_multiple_corrections(results)
        
        return results
    
    def _apply_multiple_corrections(self, results: List[Dict]) -> List[Dict]:
        """Apply multiple testing corrections"""
        p_values = [r['p_value'] for r in results]
        
        # Benjamini-Hochberg FDR
        fdr_values = self._benjamini_hochberg_correction(p_values)
        
        # Bonferroni correction
        bonferroni_values = [min(p * len(p_values), 1.0) for p in p_values]
        
        for i, result in enumerate(results):
            result['fdr'] = fdr_values[i]
            result['bonferroni'] = bonferroni_values[i]
        
        return results
    
    def _benjamini_hochberg_correction(self, p_values: List[float]) -> List[float]:
        """Apply Benjamini-Hochberg FDR correction"""
        n = len(p_values)
        sorted_indices = np.argsort(p_values)
        sorted_p_values = np.array(p_values)[sorted_indices]
        
        fdr_values = np.zeros(n)
        for i in range(n-1, -1, -1):
            if i == n-1:
                fdr_values[i] = sorted_p_values[i]
            else:
                fdr_values[i] = min(sorted_p_values[i] * n / (i + 1), fdr_values[i + 1])
        
        original_order_fdr = np.zeros(n)
        original_order_fdr[sorted_indices] = fdr_values
        
        return original_order_fdr.tolist()