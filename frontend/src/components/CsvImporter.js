import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Alert,
} from '@mui/material';
import api from '../services/api';

const FILE_TYPES = [
  { key: 'management_entities', label: 'Management Entities' },
  { key: 'master_funds', label: 'Master Funds' },
  { key: 'subfunds', label: 'Subfunds' },
  { key: 'legal_entities', label: 'Legal Entities' },
  { key: 'share_classes', label: 'Share Classes' },
];

const CsvImporter = () => {
  const [selectedFiles, setSelectedFiles] = useState({});
  const [previews, setPreviews] = useState({});
  const [status, setStatus] = useState({});

  const handleFileChange = (key, file) => {
    setSelectedFiles((s) => ({ ...s, [key]: file }));

    // create a simple preview (first 3 lines)
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split(/\r?\n/).filter(Boolean).slice(0, 4);
      const parsed = lines.map((l) => l.split(','));
      setPreviews((p) => ({ ...p, [key]: parsed }));
    };
    reader.readAsText(file);
  };

  const handleUpload = async (key) => {
    const file = selectedFiles[key];
    if (!file) {
      setStatus((s) => ({ ...s, [key]: { error: 'No file selected' } }));
      return;
    }

    const form = new FormData();
    form.append('file', file);
    form.append('target', key);

    try {
      setStatus((s) => ({ ...s, [key]: { loading: true } }));
      // Use axios instance but override header for multipart
      await api.post('/ingest/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStatus((s) => ({ ...s, [key]: { success: 'Uploaded and ingested' } }));
    } catch (err) {
      console.error(err);
      setStatus((s) => ({ ...s, [key]: { error: err.response?.data?.detail || err.message } }));
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }} elevation={3}>
        <Typography variant="h5" gutterBottom>
          CSV Importer
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Upload any of the five supported CSV datasets and choose which dataset to ingest into the graph.
        </Typography>

        <Grid container spacing={2}>
          {FILE_TYPES.map((ft) => (
            <Grid item xs={12} md={6} key={ft.key}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1">{ft.label}</Typography>
                <Box sx={{ mt: 1, mb: 1 }}>
                  <input
                    accept=".csv"
                    id={`file-${ft.key}`}
                    type="file"
                    onChange={(e) => handleFileChange(ft.key, e.target.files[0])}
                  />
                </Box>

                {previews[ft.key] && (
                  <Box sx={{ maxHeight: 160, overflow: 'auto', mb: 1 }}>
                    <Table size="small">
                      <TableBody>
                        {previews[ft.key].map((row, i) => (
                          <TableRow key={i}>
                            {row.map((cell, j) => (
                              <TableCell key={j} sx={{ p: 0.5 }}>{cell}</TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </Box>
                )}

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button variant="contained" onClick={() => handleUpload(ft.key)}>Upload & Insert</Button>
                  <Button onClick={() => { setSelectedFiles((s) => ({ ...s, [ft.key]: null })); setPreviews((p) => ({ ...p, [ft.key]: null })); setStatus((s) => ({ ...s, [ft.key]: null })); }}>Clear</Button>
                </Box>

                {status[ft.key]?.loading && <Typography variant="body2">Uploading...</Typography>}
                {status[ft.key]?.success && <Alert severity="success" sx={{ mt: 1 }}>{status[ft.key].success}</Alert>}
                {status[ft.key]?.error && <Alert severity="error" sx={{ mt: 1 }}>{status[ft.key].error}</Alert>}
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Container>
  );
};

export default CsvImporter;
