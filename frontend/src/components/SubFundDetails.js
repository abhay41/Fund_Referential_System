import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Grid,
  Box,
  Chip,
  Button,
  Divider,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  AccountTree as HierarchyIcon,
  ArrowBack as BackIcon,
  Business as BusinessIcon,
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { subfundAPI } from '../services/api';

const SubFundDetails = () => {
  const { subfundId } = useParams();
  const navigate = useNavigate();
  const [subfund, setSubfund] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSubfundDetails = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await subfundAPI.getSubFundById(subfundId);
      setSubfund(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch subfund details');
    } finally {
      setLoading(false);
    }
  }, [subfundId]);

  useEffect(() => {
    fetchSubfundDetails();
  }, [fetchSubfundDetails]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'CLOSED':
        return 'error';
      case 'SUSPENDED':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<BackIcon />} onClick={() => navigate(-1)} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Container>
    );
  }

  if (!subfund) {
    return null;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link underline="hover" color="inherit" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          Home
        </Link>
        {subfund.parent_fund && (
          <Link 
            underline="hover" 
            color="inherit" 
            onClick={() => navigate(`/fund/${subfund.parent_fund.fund_id}`)} 
            style={{ cursor: 'pointer' }}
          >
            {subfund.parent_fund.fund_name}
          </Link>
        )}
        <Typography color="text.primary">SubFund Details</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          SubFund: {subfund.subfund_id}
        </Typography>
        <Box>
          <Button
            startIcon={<HierarchyIcon />}
            variant="contained"
            onClick={() => navigate(`/subfund-visualization/${subfund.subfund_id}`)}
            sx={{ mr: 1 }}
          >
            View Hierarchy
          </Button>
          <Button startIcon={<BackIcon />} onClick={() => navigate(-1)}>
            Back
          </Button>
        </Box>
      </Box>

      {/* Basic Information */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <AccountBalanceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Basic Information
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              SubFund ID
            </Typography>
            <Typography variant="body1">{subfund.subfund_id}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              ISIN (Sub)
            </Typography>
            <Typography variant="body1">{subfund.isin_sub}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              Currency
            </Typography>
            <Typography variant="body1">{subfund.currency}</Typography>
          </Grid>
          {subfund.nav && (
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                NAV
              </Typography>
              <Typography variant="body1">{subfund.nav.toFixed(2)}</Typography>
            </Grid>
          )}
          {subfund.aum && (
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                AUM
              </Typography>
              <Typography variant="body1">{subfund.aum.toLocaleString()}</Typography>
            </Grid>
          )}
          {subfund.status && (
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Status
              </Typography>
              <Chip label={subfund.status} color={getStatusColor(subfund.status)} size="small" />
            </Grid>
          )}
        </Grid>
      </Paper>

      {/* Parent Fund */}
      {subfund.parent_fund && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            <AccountBalanceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Parent Fund
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Fund ID
              </Typography>
              <Typography variant="body1">{subfund.parent_fund.fund_id}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Fund Code
              </Typography>
              <Typography variant="body1">{subfund.parent_fund.fund_code}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Fund Name
              </Typography>
              <Typography variant="body1">{subfund.parent_fund.fund_name}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Fund Type
              </Typography>
              <Chip label={subfund.parent_fund.fund_type} variant="outlined" size="small" />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => navigate(`/fund/${subfund.parent_fund.fund_id}`)}
              >
                View Parent Fund Details
              </Button>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Management Entity */}
      {subfund.management_entity && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            <BusinessIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Management Entity
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Management ID
              </Typography>
              <Typography variant="body1">{subfund.management_entity.mgmt_id}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Registration Number
              </Typography>
              <Typography variant="body1">{subfund.management_entity.registration_no}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Domicile
              </Typography>
              <Typography variant="body1">{subfund.management_entity.domicile}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Entity Type
              </Typography>
              <Typography variant="body1">{subfund.management_entity.entity_type}</Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Share Classes */}
      {subfund.share_classes && subfund.share_classes.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Share Classes ({subfund.share_classes.length})
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>ID</strong></TableCell>
                  <TableCell><strong>ISIN</strong></TableCell>
                  <TableCell><strong>Currency</strong></TableCell>
                  <TableCell><strong>Distribution</strong></TableCell>
                  <TableCell><strong>NAV</strong></TableCell>
                  <TableCell><strong>AUM</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {subfund.share_classes.map((sc) => (
                  <TableRow key={sc.sc_id}>
                    <TableCell>{sc.sc_id}</TableCell>
                    <TableCell>{sc.isin_sc}</TableCell>
                    <TableCell>{sc.currency}</TableCell>
                    <TableCell>{sc.distribution}</TableCell>
                    <TableCell>{sc.nav?.toFixed(2)}</TableCell>
                    <TableCell>{sc.aum?.toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip label={sc.status || 'N/A'} size="small" color={getStatusColor(sc.status)} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Container>
  );
};

export default SubFundDetails;
