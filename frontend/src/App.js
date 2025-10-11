import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import Header from './components/Header';
import FundVisualization from './components/FundVisualization';
import FundSearch from './components/FundSearch';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={<FundSearch />} />
          <Route path="/visualization/:fundId" element={<FundVisualization />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;