import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import io

class MultiOmicsService:
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA()
    
    def integrate_methylation_expression(
        self,
        methylation_data: bytes,
        expression_data: bytes,
        phenotype_data: bytes,
        phenotype_column: str
    ) -> Dict:
        """Integrate methylation and gene expression data"""
        
        # Load data
        meth_df = pd.read_csv(io.BytesIO(methylation_data), sep='\t', index_col=0)
        expr_df = pd.read_csv(io.BytesIO(expression_data), sep='\t', index_col=0)
        pheno_df = pd.read_csv(io.BytesIO(phenotype_data), index_col=0)
        
        # Align samples
        common_samples = set(meth_df.columns) & set(expr_df.columns) & set(pheno_df.index)
        common_samples = list(common_samples)
        
        meth_aligned = meth_df[common_samples]
        expr_aligned = expr_df[common_samples]
        pheno_aligned = pheno_df.loc[common_samples]
        
        # Perform integration analysis
        integration_results = self._run_integration_analysis(
            meth_aligned, expr_aligned, pheno_aligned, phenotype_column
        )
        
        return integration_results
    
    def _run_integration_analysis(
        self,
        methylation: pd.DataFrame,
        expression: pd.DataFrame,
        phenotype: pd.DataFrame,
        phenotype_column: str
    ) -> Dict:
        """Run multi-omics integration analysis"""
        
        results = {
            "sample_count": len(methylation.columns),
            "methylation_features": len(methylation),
            "expression_features": len(expression),
            "correlations": [],
            "pca_results": {},
            "differential_pairs": []
        }
        
        # Calculate methylation-expression correlations
        correlations = self._calculate_meth_expr_correlations(methylation, expression)
        results["correlations"] = correlations[:100]  # Top 100
        
        # PCA analysis
        pca_results = self._perform_joint_pca(methylation, expression)
        results["pca_results"] = pca_results
        
        # Find differential pairs
        differential_pairs = self._find_differential_pairs(
            methylation, expression, phenotype, phenotype_column
        )
        results["differential_pairs"] = differential_pairs[:50]  # Top 50
        
        return results
    
    def _calculate_meth_expr_correlations(
        self, 
        methylation: pd.DataFrame, 
        expression: pd.DataFrame
    ) -> List[Dict]:
        """Calculate correlations between methylation and expression"""
        correlations = []
        
        # Sample subset for performance
        meth_subset = methylation.head(100)
        expr_subset = expression.head(100)
        
        for meth_id in meth_subset.index:
            for expr_id in expr_subset.index:
                try:
                    meth_values = meth_subset.loc[meth_id]
                    expr_values = expr_subset.loc[expr_id]
                    
                    # Remove NaN values
                    valid_mask = ~(meth_values.isna() | expr_values.isna())
                    if valid_mask.sum() < 5:
                        continue
                    
                    correlation = np.corrcoef(
                        meth_values[valid_mask], 
                        expr_values[valid_mask]
                    )[0, 1]
                    
                    if not np.isnan(correlation):
                        correlations.append({
                            "methylation_id": meth_id,
                            "expression_id": expr_id,
                            "correlation": float(correlation),
                            "abs_correlation": abs(float(correlation))
                        })
                except:
                    continue
        
        # Sort by absolute correlation
        correlations.sort(key=lambda x: x["abs_correlation"], reverse=True)
        return correlations
    
    def _perform_joint_pca(
        self, 
        methylation: pd.DataFrame, 
        expression: pd.DataFrame
    ) -> Dict:
        """Perform joint PCA analysis"""
        try:
            # Combine data (sample subset)
            meth_subset = methylation.head(50).T  # Transpose for samples as rows
            expr_subset = expression.head(50).T
            
            # Standardize
            meth_scaled = self.scaler.fit_transform(meth_subset.fillna(0))
            expr_scaled = self.scaler.fit_transform(expr_subset.fillna(0))
            
            # Joint matrix
            joint_data = np.hstack([meth_scaled, expr_scaled])
            
            # PCA
            pca = PCA(n_components=min(10, joint_data.shape[1]))
            pca_result = pca.fit_transform(joint_data)
            
            return {
                "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
                "cumulative_variance": np.cumsum(pca.explained_variance_ratio_).tolist(),
                "n_components": pca.n_components_,
                "sample_coordinates": pca_result.tolist()
            }
        except:
            return {"error": "PCA analysis failed"}
    
    def _find_differential_pairs(
        self,
        methylation: pd.DataFrame,
        expression: pd.DataFrame,
        phenotype: pd.DataFrame,
        phenotype_column: str
    ) -> List[Dict]:
        """Find methylation-expression pairs differential between phenotypes"""
        differential_pairs = []
        
        # Get phenotype groups
        phenotype_values = phenotype[phenotype_column]
        unique_phenotypes = phenotype_values.unique()
        
        if len(unique_phenotypes) != 2:
            return []
        
        group1_samples = phenotype_values[phenotype_values == unique_phenotypes[0]].index
        group2_samples = phenotype_values[phenotype_values == unique_phenotypes[1]].index
        
        # Sample subset for performance
        meth_subset = methylation.head(20)
        expr_subset = expression.head(20)
        
        for meth_id in meth_subset.index:
            for expr_id in expr_subset.index:
                try:
                    # Calculate correlations in each group
                    meth_values = meth_subset.loc[meth_id]
                    expr_values = expr_subset.loc[expr_id]
                    
                    # Group 1 correlation
                    g1_meth = meth_values[group1_samples].dropna()
                    g1_expr = expr_values[group1_samples].dropna()
                    common_g1 = g1_meth.index.intersection(g1_expr.index)
                    
                    if len(common_g1) < 3:
                        continue
                    
                    corr_g1 = np.corrcoef(g1_meth[common_g1], g1_expr[common_g1])[0, 1]
                    
                    # Group 2 correlation
                    g2_meth = meth_values[group2_samples].dropna()
                    g2_expr = expr_values[group2_samples].dropna()
                    common_g2 = g2_meth.index.intersection(g2_expr.index)
                    
                    if len(common_g2) < 3:
                        continue
                    
                    corr_g2 = np.corrcoef(g2_meth[common_g2], g2_expr[common_g2])[0, 1]
                    
                    if not (np.isnan(corr_g1) or np.isnan(corr_g2)):
                        differential_pairs.append({
                            "methylation_id": meth_id,
                            "expression_id": expr_id,
                            "correlation_group1": float(corr_g1),
                            "correlation_group2": float(corr_g2),
                            "correlation_difference": abs(float(corr_g1 - corr_g2))
                        })
                except:
                    continue
        
        # Sort by correlation difference
        differential_pairs.sort(key=lambda x: x["correlation_difference"], reverse=True)
        return differential_pairs