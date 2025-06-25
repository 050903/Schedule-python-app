import React, { useState } from 'react';
import { Container, Typography, Box, Tabs, Tab } from '@mui/material';
import FileUpload from './components/FileUpload';
import AnalysisForm from './components/AnalysisForm';
import ResultsView from './components/ResultsView';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [files, setFiles] = useState([]);
  const [analyses, setAnalyses] = useState([]);

  return (
    <Container maxWidth="lg">
      <Typography variant="h3" component="h1" gutterBottom sx={{ mt: 4, mb: 4 }}>
        EpiMap X - EWAS Platform
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Upload Data" />
          <Tab label="Run Analysis" />
          <Tab label="View Results" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <FileUpload files={files} setFiles={setFiles} />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <AnalysisForm files={files} analyses={analyses} setAnalyses={setAnalyses} />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <ResultsView analyses={analyses} />
      </TabPanel>
    </Container>
  );
}

export default App;