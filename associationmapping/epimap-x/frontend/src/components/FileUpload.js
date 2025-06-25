import React, { useState } from 'react';
import { Box, Button, Typography, List, ListItem, ListItemText, Alert } from '@mui/material';
import { uploadFile, getFiles } from '../services/api';

function FileUpload({ files, setFiles }) {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileUpload = async (event, fileType) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage('');

    try {
      const response = await uploadFile(file, fileType);
      setMessage(`${fileType} file uploaded successfully!`);
      
      // Refresh file list
      const updatedFiles = await getFiles();
      setFiles(updatedFiles);
    } catch (error) {
      setMessage(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Upload Data Files
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6">Epigenome Data (.tsv)</Typography>
        <input
          type="file"
          accept=".tsv,.csv"
          onChange={(e) => handleFileUpload(e, 'epigenome')}
          disabled={uploading}
          style={{ margin: '10px 0' }}
        />
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6">Phenotype Data (.csv)</Typography>
        <input
          type="file"
          accept=".csv,.tsv"
          onChange={(e) => handleFileUpload(e, 'phenotype')}
          disabled={uploading}
          style={{ margin: '10px 0' }}
        />
      </Box>

      {message && (
        <Alert severity={message.includes('failed') ? 'error' : 'success'} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Typography variant="h6" gutterBottom>
        Uploaded Files
      </Typography>
      <List>
        {files.map((file) => (
          <ListItem key={file.file_id}>
            <ListItemText
              primary={file.filename}
              secondary={`Type: ${file.type} | Size: ${file.size_bytes} bytes`}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}

export default FileUpload;