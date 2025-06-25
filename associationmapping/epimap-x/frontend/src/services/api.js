import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadFile = async (file, fileType) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const endpoint = fileType === 'epigenome' ? '/files/upload/epigenome' : '/files/upload/phenotype';
  const response = await api.post(endpoint, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return response.data;
};

export const getFiles = async () => {
  const response = await api.get('/files/');
  return response.data;
};

export const submitAnalysis = async (analysisData) => {
  const response = await api.post('/analysis/ewas', analysisData);
  return response.data;
};

export const getAnalysisStatus = async (analysisId) => {
  const response = await api.get(`/analysis/${analysisId}/status`);
  return response.data;
};

export const getAllAnalyses = async () => {
  const response = await api.get('/analysis/all');
  return response.data;
};

export const getManhattanData = async (analysisId) => {
  const response = await api.get(`/results/${analysisId}/manhattan`);
  return response.data;
};

export const getQQPlotData = async (analysisId) => {
  const response = await api.get(`/results/${analysisId}/qqplot_data`);
  return response.data;
};

export const getResultsTable = async (analysisId) => {
  const response = await api.get(`/results/${analysisId}/table`);
  return response.data;
};