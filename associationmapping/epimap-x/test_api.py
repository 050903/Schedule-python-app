#!/usr/bin/env python3
"""
Script để test API của EpiMap X
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_file_upload():
    """Test upload files"""
    print("=== Testing File Upload ===")
    
    # Upload epigenome file
    with open("sample_data/epigenome_data.tsv", "rb") as f:
        files = {"file": ("epigenome_data.tsv", f, "text/tab-separated-values")}
        response = requests.post(f"{BASE_URL}/files/upload/epigenome", files=files)
        print(f"Epigenome upload: {response.status_code}")
        if response.status_code == 200:
            epigenome_file_id = response.json()["file_id"]
            print(f"Epigenome file ID: {epigenome_file_id}")
        else:
            print(f"Error: {response.text}")
            return None, None
    
    # Upload phenotype file
    with open("sample_data/phenotype_data.csv", "rb") as f:
        files = {"file": ("phenotype_data.csv", f, "text/csv")}
        response = requests.post(f"{BASE_URL}/files/upload/phenotype", files=files)
        print(f"Phenotype upload: {response.status_code}")
        if response.status_code == 200:
            phenotype_file_id = response.json()["file_id"]
            print(f"Phenotype file ID: {phenotype_file_id}")
        else:
            print(f"Error: {response.text}")
            return epigenome_file_id, None
    
    return epigenome_file_id, phenotype_file_id

def test_analysis(epigenome_file_id, phenotype_file_id):
    """Test EWAS analysis"""
    print("\n=== Testing EWAS Analysis ===")
    
    analysis_request = {
        "epigenome_file_id": epigenome_file_id,
        "phenotype_file_id": phenotype_file_id,
        "phenotype_column": "disease_status",
        "covariates": ["age", "sex"],
        "model_type": "linear_regression"
    }
    
    response = requests.post(f"{BASE_URL}/analysis/ewas", json=analysis_request)
    print(f"Analysis submission: {response.status_code}")
    
    if response.status_code == 200:
        analysis_id = response.json()["analysis_id"]
        print(f"Analysis ID: {analysis_id}")
        
        # Check status
        for i in range(10):  # Wait up to 10 seconds
            response = requests.get(f"{BASE_URL}/analysis/{analysis_id}/status")
            if response.status_code == 200:
                status_data = response.json()
                print(f"Status: {status_data['status']} - Progress: {status_data['progress']}%")
                
                if status_data['status'] in ['COMPLETED', 'FAILED']:
                    break
            time.sleep(1)
        
        return analysis_id
    else:
        print(f"Error: {response.text}")
        return None

def test_results(analysis_id):
    """Test results retrieval"""
    print("\n=== Testing Results Retrieval ===")
    
    # Get Manhattan data
    response = requests.get(f"{BASE_URL}/results/{analysis_id}/manhattan")
    if response.status_code == 200:
        manhattan_data = response.json()
        print(f"Manhattan data points: {len(manhattan_data)}")
    else:
        print(f"Manhattan data error: {response.text}")
    
    # Get QQ plot data
    response = requests.get(f"{BASE_URL}/results/{analysis_id}/qqplot_data")
    if response.status_code == 200:
        qq_data = response.json()
        print(f"QQ plot data points: {len(qq_data)}")
    else:
        print(f"QQ plot data error: {response.text}")
    
    # Get results table
    response = requests.get(f"{BASE_URL}/results/{analysis_id}/table")
    if response.status_code == 200:
        table_data = response.json()
        print(f"Results table rows: {len(table_data)}")
        if table_data:
            print(f"Top result: {table_data[0]}")
    else:
        print(f"Results table error: {response.text}")

def main():
    print("Testing EpiMap X API")
    
    # Test file upload
    epigenome_file_id, phenotype_file_id = test_file_upload()
    
    if epigenome_file_id and phenotype_file_id:
        # Test analysis
        analysis_id = test_analysis(epigenome_file_id, phenotype_file_id)
        
        if analysis_id:
            # Test results
            test_results(analysis_id)
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    main()