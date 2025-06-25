import React, { useState, useEffect } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Button, Paper } from '@mui/material';
import Plot from 'react-plotly.js';
import { getAnalysisStatus, getManhattanData, getQQPlotData } from '../services/api';

function ResultsView({ analyses }) {
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [manhattanData, setManhattanData] = useState([]);
  const [qqData, setQQData] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadResults = async (analysisId) => {
    setLoading(true);
    try {
      const [manhattan, qq] = await Promise.all([
        getManhattanData(analysisId),
        getQQPlotData(analysisId)
      ]);
      setManhattanData(manhattan);
      setQQData(qq);
    } catch (error) {
      console.error('Failed to load results:', error);
    } finally {
      setLoading(false);
    }
  };

  const manhattanPlot = {
    data: [{
      x: manhattanData.map(d => d.pos),
      y: manhattanData.map(d => d.log10_p),
      mode: 'markers',
      type: 'scatter',
      text: manhattanData.map(d => d.cpg_id),
      marker: { size: 4 }
    }],
    layout: {
      title: 'Manhattan Plot',
      xaxis: { title: 'Genomic Position' },
      yaxis: { title: '-log10(p-value)' }
    }
  };

  const qqPlot = {
    data: [{
      x: qqData.map(d => d.expected),
      y: qqData.map(d => d.observed),
      mode: 'markers',
      type: 'scatter',
      marker: { size: 4 }
    }],
    layout: {
      title: 'QQ Plot',
      xaxis: { title: 'Expected -log10(p)' },
      yaxis: { title: 'Observed -log10(p)' }
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analysis Results
      </Typography>

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Paper sx={{ p: 2, minWidth: 300 }}>
          <Typography variant="h6" gutterBottom>
            Analyses
          </Typography>
          <List>
            {analyses.map((analysis) => (
              <ListItem key={analysis.analysis_id}>
                <ListItemText
                  primary={analysis.name}
                  secondary={`Status: ${analysis.status}`}
                />
                <Button
                  onClick={() => {
                    setSelectedAnalysis(analysis);
                    loadResults(analysis.analysis_id);
                  }}
                  variant="outlined"
                  size="small"
                >
                  View
                </Button>
              </ListItem>
            ))}
          </List>
        </Paper>

        <Box sx={{ flex: 1 }}>
          {selectedAnalysis && (
            <>
              <Typography variant="h6" gutterBottom>
                Results for: {selectedAnalysis.name}
              </Typography>
              
              {loading ? (
                <Typography>Loading results...</Typography>
              ) : (
                <>
                  <Box sx={{ mb: 4 }}>
                    <Plot
                      data={manhattanPlot.data}
                      layout={manhattanPlot.layout}
                      style={{ width: '100%', height: '400px' }}
                    />
                  </Box>
                  
                  <Box>
                    <Plot
                      data={qqPlot.data}
                      layout={qqPlot.layout}
                      style={{ width: '100%', height: '400px' }}
                    />
                  </Box>
                </>
              )}
            </>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default ResultsView;