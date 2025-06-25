import numpy as np
import pandas as pd
from typing import List, Dict, Any

class VisualizationUtils:
    @staticmethod
    def prepare_manhattan_data(results: List[Dict]) -> List[Dict]:
        """Prepare data for Manhattan plot visualization"""
        manhattan_data = []
        
        for result in results:
            # Calculate -log10(p-value)
            log10_p = -np.log10(max(result['p_value'], 1e-300))
            
            manhattan_data.append({
                "chrom": result['chromosome'],
                "pos": result['position'],
                "p_value": result['p_value'],
                "log10_p": log10_p,
                "cpg_id": result['cpg_id'],
                "beta": result['beta']
            })
        
        # Sort by chromosome and position
        manhattan_data.sort(key=lambda x: (x['chrom'], x['pos']))
        
        return manhattan_data
    
    @staticmethod
    def prepare_qq_plot_data(p_values: List[float]) -> List[Dict]:
        """Prepare data for QQ plot visualization"""
        # Remove NaN and invalid p-values
        valid_p_values = [p for p in p_values if not np.isnan(p) and 0 < p <= 1]
        
        if not valid_p_values:
            return []
        
        # Sort p-values
        observed_p = np.sort(valid_p_values)
        n = len(observed_p)
        
        # Calculate expected p-values under null hypothesis
        expected_p = np.arange(1, n + 1) / (n + 1)
        
        qq_data = []
        for i in range(n):
            qq_data.append({
                "expected": -np.log10(expected_p[i]),
                "observed": -np.log10(max(observed_p[i], 1e-300))
            })
        
        return qq_data
    
    @staticmethod
    def calculate_genomic_inflation(p_values: List[float]) -> float:
        """Calculate genomic inflation factor (lambda)"""
        valid_p_values = [p for p in p_values if not np.isnan(p) and 0 < p <= 1]
        
        if len(valid_p_values) < 100:
            return 1.0
        
        # Convert to chi-square statistics
        chi_square_stats = [-2 * np.log(p) for p in valid_p_values]
        
        # Calculate median
        median_chi_square = np.median(chi_square_stats)
        
        # Expected median under null (chi-square with 1 df)
        expected_median = 0.4549  # qchisq(0.5, df=1)
        
        # Genomic inflation factor
        lambda_gc = median_chi_square / expected_median
        
        return lambda_gc
    
    @staticmethod
    def identify_significant_cpgs(results: List[Dict], p_threshold: float = 5e-8, fdr_threshold: float = 0.05) -> Dict[str, List[Dict]]:
        """Identify significant CpGs based on p-value and FDR thresholds"""
        significant_results = {
            "genome_wide_significant": [],
            "fdr_significant": []
        }
        
        for result in results:
            if result['p_value'] < p_threshold:
                significant_results["genome_wide_significant"].append(result)
            
            if result.get('fdr', 1.0) < fdr_threshold:
                significant_results["fdr_significant"].append(result)
        
        return significant_results