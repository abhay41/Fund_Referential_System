import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  AccountBalance as FundIcon,
  Assessment as AssessmentIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Business as ManagementIcon,
} from '@mui/icons-material';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fundAPI, statisticsAPI } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalFunds: 0,
    totalManagementEntities: 0,
    activeFunds: 0,
    inactiveFunds: 0,
    fundsByType: [],
    recentFunds: [],
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Use the new combined statistics API
      const statsResponse = await statisticsAPI.getDashboardStatistics();
      const data = statsResponse.data;
      
      // Fetch recent funds separately
      const fundsResponse = await fundAPI.searchFunds({}, 1, 5);
      const recentFunds = fundsResponse.data.funds || [];

      setStats({
        totalFunds: data.total_funds || 0,
        totalManagementEntities: data.total_management_entities || 0,
        activeFunds: data.active_funds || 0,
        inactiveFunds: data.inactive_funds || 0,
        fundsByType: data.funds_by_type || [],
        recentFunds: recentFunds,
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button onClick={fetchDashboardData} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Fund Referential Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of all funds and management entities
        </Typography>
      </Box>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Button
            variant="contained"
            size="large"
            fullWidth
            startIcon={<SearchIcon />}
            onClick={() => navigate('/search')}
            sx={{ py: 2 }}
          >
            Search Funds
          </Button>
        </Grid>
        <Grid item xs={12} md={6}>
          <Button
            variant="outlined"
            size="large"
            fullWidth
            startIcon={<AddIcon />}
            onClick={() => navigate('/onboarding')}
            sx={{ py: 2 }}
          >
            Onboard New Fund
          </Button>
        </Grid>
      </Grid>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <FundIcon sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Total Funds
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalFunds}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ManagementIcon sx={{ fontSize: 40, color: '#9c27b0', mr: 2 }} />
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Management Entities
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalManagementEntities}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ fontSize: 40, color: '#4caf50', mr: 2 }} />
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Active Funds
                  </Typography>
                  <Typography variant="h4">
                    {stats.activeFunds}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssessmentIcon sx={{ fontSize: 40, color: '#ff9800', mr: 2 }} />
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Inactive Funds
                  </Typography>
                  <Typography variant="h4">
                    {stats.inactiveFunds}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Funds by Type - Pie Chart */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Funds by Type
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.fundsByType}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {stats.fundsByType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Funds by Type - Bar Chart */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Fund Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.fundsByType}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#1976d2" name="Number of Funds" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Funds */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Funds
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <List>
          {stats.recentFunds.map((fund, index) => (
            <React.Fragment key={fund.fund_id}>
              <ListItem
                button
                onClick={() => navigate(`/fund/${fund.fund_id}`)}
                sx={{
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body1">
                        {fund.fund_name}
                      </Typography>
                      <Box
                        sx={{
                          px: 1,
                          py: 0.5,
                          borderRadius: 1,
                          bgcolor: fund.status === 'ACTIVE' ? 'success.light' : 'warning.light',
                          color: fund.status === 'ACTIVE' ? 'success.dark' : 'warning.dark',
                        }}
                      >
                        <Typography variant="caption">
                          {fund.status}
                        </Typography>
                      </Box>
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {fund.fund_code} | {fund.fund_type} | {fund.base_currency}
                      </Typography>
                      {fund.isin_master && (
                        <Typography variant="caption" color="text.secondary">
                          ISIN: {fund.isin_master}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
              {index < stats.recentFunds.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
        {stats.recentFunds.length === 0 && (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
            No funds available
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default Dashboard;
