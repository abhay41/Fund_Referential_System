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
  Card,
  CardContent,
  CardActions,
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
  AccountTree,
  ArrowBack as BackIcon,
  Business as BusinessIcon,
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { fundAPI } from '../services/api';

const FundDetails = () => {
  const { fundId } = useParams();
  const navigate = useNavigate();
  const [fund, setFund] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchFundDetails = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fundAPI.getFundById(fundId);
      setFund(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch fund details');
    } finally {
      setLoading(false);
    }
  }, [fundId]);

  useEffect(() => {
    fetchFundDetails();
  }, [fetchFundDetails]);

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
        <Button startIcon={<BackIcon />} onClick={() => navigate('/')} sx={{ mt: 2 }}>
          Back to Search
        </Button>
      </Container>
    );
  }

  if (!fund) {
    return null;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link underline="hover" color="inherit" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          Home
        </Link>
        <Typography color="text.primary">Fund Details</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          {fund.fund_name}
        </Typography>
        <Box>
          <Button
            startIcon={<HierarchyIcon />}
            variant="contained"
            onClick={() => navigate(`/visualization/${fund.fund_id}`)}
            sx={{ mr: 1 }}
          >
            View Hierarchy
          </Button>
          <Button startIcon={<BackIcon />} onClick={() => navigate('/')}>
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
              Fund ID
            </Typography>
            <Typography variant="body1">{fund.fund_id}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              Fund Code
            </Typography>
            <Typography variant="body1">{fund.fund_code}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              Fund Type
            </Typography>
            <Chip label={fund.fund_type} variant="outlined" size="small" />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              Base Currency
            </Typography>
            <Typography variant="body1">{fund.base_currency}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              Domicile
            </Typography>
            <Typography variant="body1">{fund.domicile}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="subtitle2" color="text.secondary">
              Status
            </Typography>
            <Chip label={fund.status} color={getStatusColor(fund.status)} size="small" />
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" color="text.secondary">
              ISIN (Master)
            </Typography>
            <Typography variant="body1">{fund.isin_master}</Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Management Entity */}
      {fund.management_entity && (
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
              <Typography variant="body1">{fund.management_entity.mgmt_id}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Registration Number
              </Typography>
              <Typography variant="body1">{fund.management_entity.registration_no}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Domicile
              </Typography>
              <Typography variant="body1">{fund.management_entity.domicile}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Entity Type
              </Typography>
              <Typography variant="body1">{fund.management_entity.entity_type}</Typography>
            </Grid>
            {fund.management_entity.legal_entity && (
              <>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" sx={{ mt: 1 }}>
                    Legal Entity
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Legal Name
                  </Typography>
                  <Typography variant="body1">{fund.management_entity.legal_entity.legal_name}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    LEI
                  </Typography>
                  <Typography variant="body1">{fund.management_entity.legal_entity.lei}</Typography>
                </Grid>
              </>
            )}
          </Grid>
        </Paper>
      )}

      {/* Share Classes */}
      {fund.share_classes && fund.share_classes.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Share Classes ({fund.share_classes.length})
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
                {fund.share_classes.map((sc) => (
                  <TableRow key={sc.sc_id}>
                    <TableCell>{sc.sc_id}</TableCell>
                    <TableCell>{sc.isin_sc}</TableCell>
                    <TableCell>{sc.currency}</TableCell>
                    <TableCell>{sc.distribution}</TableCell>
                    <TableCell>{sc.nav?.toFixed(2)}</TableCell>
                    <TableCell>{sc.aum?.toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip label={sc.status} size="small" color={getStatusColor(sc.status)} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* SubFunds */}
      {fund.subfunds && fund.subfunds.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <AccountTree sx={{ mr: 1, verticalAlign: 'middle' }} />
            SubFunds ({fund.subfunds.length})
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            {fund.subfunds.map((subfund) => (
              <Grid item xs={12} sm={6} md={4} key={subfund.subfund_id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {subfund.subfund_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      ISIN: {subfund.isin_sub}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Currency: {subfund.currency}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => navigate(`/subfund/${subfund.subfund_id}`)}
                      startIcon={<VisibilityIcon />}
                    >
                      View Details
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Container>
  );
};

export default FundDetails;
