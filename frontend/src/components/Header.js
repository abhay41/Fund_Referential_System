import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Fund Referential
        </Typography>
        <Button color="inherit" component={RouterLink} to="/">
          Search
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default Header;