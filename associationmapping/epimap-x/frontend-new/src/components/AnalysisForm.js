import React, { useState } from 'react';
import { Box, Button, TextField, Select, MenuItem, FormControl, InputLabel, Typography, Alert } from '@mui/material';
import { submitAnalysis } from '../services/api';

function AnalysisForm({ files, analyses, setAnalyses }) {
  const [formData, setFormData] = useState({
    epigenome_file_id: '',
    phenotype_file_id: '',
    phenotype_column: 'disease_status',
    covariates: 'age,sex'
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const epigenomeFiles = files.filter(f => f.type === 'epigenome');
  const phenotypeFiles = files.filter(f => f.type === 'phenotype');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');

    try {
      const analysisData = {
        ...formData,
        epigenome_file_id: parseInt(formData.epigenome_file_id),
        phenotype_file_id: parseInt(formData.phenotype_file_id),
        covariates: formData.covariates.split(',').map(s => s.trim())
      };

      const response = await submitAnalysis(analysisData);
      setMessage(`Analysis submitted successfully! ID: ${response.analysis_id}`);
      
      // Add to analyses list
      setAnalyses([...analyses, {
        analysis_id: response.analysis_id,
        name: `EWAS_${formData.phenotype_column}`,
        status: 'PENDING'
      }]);
    } catch (error) {
      setMessage(`Analysis failed: ${error.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Run EWAS Analysis
      </Typography>

      <form onSubmit={handleSubmit}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Epigenome File</InputLabel>
          <Select
            value={formData.epigenome_file_id}
            onChange={(e) => setFormData({...formData, epigenome_file_id: e.target.value})}
            required
          >
            {epigenomeFiles.map(file => (
              <MenuItem key={file.file_id} value={file.file_id}>
                {file.filename}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Phenotype File</InputLabel>
          <Select
            value={formData.phenotype_file_id}
            onChange={(e) => setFormData({...formData, phenotype_file_id: e.target.value})}
            required
          >
            {phenotypeFiles.map(file => (
              <MenuItem key={file.file_id} value={file.file_id}>
                {file.filename}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          fullWidth
          label="Phenotype Column"
          value={formData.phenotype_column}
          onChange={(e) => setFormData({...formData, phenotype_column: e.target.value})}
          sx={{ mb: 2 }}
          required
        />

        <TextField
          fullWidth
          label="Covariates (comma-separated)"
          value={formData.covariates}
          onChange={(e) => setFormData({...formData, covariates: e.target.value})}
          sx={{ mb: 2 }}
        />

        <Button
          type="submit"
          variant="contained"
          disabled={submitting || !formData.epigenome_file_id || !formData.phenotype_file_id}
          sx={{ mb: 2 }}
        >
          {submitting ? 'Submitting...' : 'Run Analysis'}
        </Button>
      </form>

      {message && (
        <Alert severity={message.includes('failed') ? 'error' : 'success'}>
          {message}
        </Alert>
      )}
    </Box>
  );
}

export default AnalysisForm;