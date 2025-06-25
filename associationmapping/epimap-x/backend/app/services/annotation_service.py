import pandas as pd
import requests
from typing import List, Dict, Optional
import asyncio
import aiohttp

class AnnotationService:
    def __init__(self):
        self.ensembl_base_url = "https://rest.ensembl.org"
        self.ucsc_base_url = "https://api.genome.ucsc.edu"
    
    async def annotate_cpgs(self, cpg_list: List[str]) -> Dict[str, Dict]:
        """Annotate CpGs with gene information"""
        annotations = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for cpg_id in cpg_list[:100]:  # Limit to avoid rate limiting
                if ':' in cpg_id:
                    chrom, pos = cpg_id.split(':')
                    tasks.append(self._get_gene_annotation(session, cpg_id, chrom, int(pos)))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for cpg_id, result in zip(cpg_list[:100], results):
                if not isinstance(result, Exception):
                    annotations[cpg_id] = result
                else:
                    annotations[cpg_id] = {"gene": "unknown", "feature": "unknown"}
        
        return annotations
    
    async def _get_gene_annotation(self, session: aiohttp.ClientSession, cpg_id: str, chrom: str, pos: int) -> Dict:
        """Get gene annotation for a single CpG"""
        try:
            # Clean chromosome name
            chrom_clean = chrom.replace('chr', '')
            
            # Query Ensembl REST API
            url = f"{self.ensembl_base_url}/overlap/region/human/{chrom_clean}:{pos}-{pos}?feature=gene"
            
            async with session.get(url, headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data:
                        gene_info = data[0]
                        return {
                            "gene": gene_info.get("external_name", "unknown"),
                            "gene_id": gene_info.get("id", "unknown"),
                            "biotype": gene_info.get("biotype", "unknown"),
                            "feature": "gene_body"
                        }
            
            return {"gene": "intergenic", "feature": "intergenic"}
            
        except Exception:
            return {"gene": "unknown", "feature": "unknown"}
    
    def get_pathway_enrichment(self, gene_list: List[str]) -> Dict:
        """Get pathway enrichment for gene list (simplified)"""
        # This would typically use KEGG, GO, or other pathway databases
        # For now, return mock enrichment results
        
        pathways = {
            "DNA_methylation": {"genes": [], "p_value": 0.001, "description": "DNA methylation process"},
            "chromatin_organization": {"genes": [], "p_value": 0.005, "description": "Chromatin organization"},
            "transcription_regulation": {"genes": [], "p_value": 0.01, "description": "Transcriptional regulation"}
        }
        
        # Mock assignment of genes to pathways
        for i, gene in enumerate(gene_list[:10]):
            pathway_key = list(pathways.keys())[i % 3]
            pathways[pathway_key]["genes"].append(gene)
        
        return pathways
    
    def get_cpg_island_annotation(self, cpg_positions: List[tuple]) -> Dict[str, str]:
        """Annotate CpGs with CpG island information"""
        annotations = {}
        
        # Mock CpG island annotation
        for chrom, pos in cpg_positions:
            cpg_id = f"{chrom}:{pos}"
            
            # Simple heuristic for demo
            if pos % 3 == 0:
                annotations[cpg_id] = "CpG_island"
            elif pos % 3 == 1:
                annotations[cpg_id] = "CpG_shore"
            else:
                annotations[cpg_id] = "open_sea"
        
        return annotations