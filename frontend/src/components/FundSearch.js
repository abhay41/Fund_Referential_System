import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemButton
} from '@mui/material';

const FundSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const navigate = useNavigate();

  const handleSearch = async () => {
    try {
      // Replace with actual search endpoint
      const response = await fetch(`http://localhost:8000/funds/search?q=${searchTerm}`);
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Error searching funds:', error);
    }
  };

  const handleResultClick = (fundId) => {
    navigate(`/visualization/${fundId}`);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Search Funds
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter fund name or ID"
            variant="outlined"
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            sx={{ minWidth: '100px' }}
          >
            Search
          </Button>
        </Box>
      </Paper>

      {searchResults.length > 0 && (
        <Paper elevation={3} sx={{ p: 2 }}>
          <List>
            {searchResults.map((fund) => (
              <ListItem key={fund.id} disablePadding>
                <ListItemButton onClick={() => handleResultClick(fund.id)}>
                  <ListItemText
                    primary={fund.name}
                    secondary={`ID: ${fund.id}`}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default FundSearch;