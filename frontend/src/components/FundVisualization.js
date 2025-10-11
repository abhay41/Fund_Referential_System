import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Breadcrumbs,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { fundAPI, managementAPI } from '../services/api';

const FundVisualization = () => {
  const { fundId } = useParams();
  const navigate = useNavigate();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [fund, setFund] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hierarchyDepth, setHierarchyDepth] = useState(2);
  const [selectedNode, setSelectedNode] = useState(null);
  const [managementModalOpen, setManagementModalOpen] = useState(false);
  const [managementFunds, setManagementFunds] = useState([]);
  const [loadingManagementFunds, setLoadingManagementFunds] = useState(false);
  const [selectedMgmtEntity, setSelectedMgmtEntity] = useState(null);

  const fetchHierarchy = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch fund details
      const fundResponse = await fundAPI.getFundById(fundId);
      setFund(fundResponse.data);

      // Fetch children hierarchy
      const childrenResponse = await fundAPI.getFundHierarchyChildren(fundId, hierarchyDepth);
      const hierarchyData = childrenResponse.data;

      // Build nodes and edges
      const newNodes = [];
      const newEdges = [];

      // Add root fund node
      const rootNode = {
        id: fundId,
        type: 'default',
        data: {
          label: (
            <div style={{ padding: '10px', textAlign: 'center' }}>
              <strong>{fundResponse.data.fund_name}</strong>
              <br />
              <small>{fundResponse.data.fund_code}</small>
              <br />
              <Chip label={fundResponse.data.fund_type} size="small" sx={{ mt: 0.5 }} />
            </div>
          ),
        },
        position: { x: 400, y: 50 },
        style: {
          background: '#1976d2',
          color: 'white',
          border: '2px solid #115293',
          borderRadius: '8px',
          width: 250,
        },
      };
      newNodes.push(rootNode);

      // Add management entity node
      if (fundResponse.data.management_entity) {
        const mgmtNode = {
          id: `mgmt_${fundResponse.data.management_entity.mgmt_id}`,
          data: {
            label: (
              <div style={{ padding: '10px', textAlign: 'center' }}>
                <strong>Management Entity</strong>
                <br />
                <small>{fundResponse.data.management_entity.mgmt_id}</small>
                <br />
                <small>{fundResponse.data.management_entity.registration_no}</small>
                <br />
                <small style={{ fontSize: '9px', color: '#e0e0e0' }}>Click to view all funds</small>
              </div>
            ),
          },
          position: { x: 100, y: 50 },
          style: {
            background: '#4caf50',
            color: 'white',
            border: '2px solid #388e3c',
            borderRadius: '8px',
            width: 200,
            cursor: 'pointer',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            transition: 'all 0.2s',
          },
        };
        newNodes.push(mgmtNode);

        newEdges.push({
          id: `e-mgmt-${fundId}`,
          source: `mgmt_${fundResponse.data.management_entity.mgmt_id}`,
          target: fundId,
          label: 'manages',
          type: 'smoothstep',
          animated: true,
          markerEnd: {
            type: MarkerType.ArrowClosed,
          },
        });
      }

      // Add share classes
      if (fundResponse.data.share_classes && fundResponse.data.share_classes.length > 0) {
        fundResponse.data.share_classes.forEach((sc, index) => {
          const scNode = {
            id: sc.sc_id,
            data: {
              label: (
                <div style={{ padding: '8px', textAlign: 'center' }}>
                  <strong>Share Class</strong>
                  <br />
                  <small>{sc.sc_id}</small>
                  <br />
                  <small>{sc.currency} - {sc.distribution}</small>
                </div>
              ),
            },
            position: { x: 700 + (index * 180), y: 50 },
            style: {
              background: '#ff9800',
              color: 'white',
              border: '2px solid #f57c00',
              borderRadius: '8px',
              width: 160,
              fontSize: '11px',
            },
          };
          newNodes.push(scNode);

          newEdges.push({
            id: `e-${fundId}-${sc.sc_id}`,
            source: fundId,
            target: sc.sc_id,
            label: 'has class',
            type: 'smoothstep',
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
          });
        });
      }

      // Add subfunds (children)
      if (hierarchyData.children && hierarchyData.children.length > 0) {
        hierarchyData.children.forEach((subfund, index) => {
          const subfundNode = {
            id: subfund.subfund_id,
            data: {
              label: (
                <div style={{ padding: '10px', textAlign: 'center' }}>
                  <strong>SubFund</strong>
                  <br />
                  <small>{subfund.subfund_id}</small>
                  <br />
                  <small>{subfund.currency}</small>
                </div>
              ),
            },
            position: { x: 300 + (index * 200), y: 220 },
            style: {
              background: '#9c27b0',
              color: 'white',
              border: '2px solid #7b1fa2',
              borderRadius: '8px',
              width: 180,
            },
          };
          newNodes.push(subfundNode);

          newEdges.push({
            id: `e-${fundId}-${subfund.subfund_id}`,
            source: fundId,
            target: subfund.subfund_id,
            label: 'parent',
            type: 'smoothstep',
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
          });
        });
      }

      setNodes(newNodes);
      setEdges(newEdges);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch hierarchy');
    } finally {
      setLoading(false);
    }
  }, [fundId, hierarchyDepth, setNodes, setEdges]);

  useEffect(() => {
    fetchHierarchy();
  }, [fetchHierarchy]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = (event, node) => {
    setSelectedNode(node);
    
    // If clicked on management entity node, fetch all funds managed by it
    if (node.id.startsWith('mgmt_')) {
      const mgmtId = node.id.replace('mgmt_', '');
      fetchManagementFunds(mgmtId);
    }
  };

  const fetchManagementFunds = async (mgmtId) => {
    setLoadingManagementFunds(true);
    setManagementModalOpen(true);
    setSelectedMgmtEntity(mgmtId);
    
    try {
      const response = await fundAPI.getFundsByManagementEntity(mgmtId, 1, 100);
      console.log('Management funds response:', response.data);
      
      // Handle both array and object responses
      let fundsData = [];
      if (Array.isArray(response.data)) {
        // Direct array response
        fundsData = response.data;
      } else if (response.data.funds) {
        // Wrapped response with funds property
        fundsData = response.data.funds;
      } else if (response.data.data) {
        // Wrapped response with data property
        fundsData = response.data.data;
      }
      
      setManagementFunds(fundsData);
      console.log('Set management funds:', fundsData.length);
    } catch (err) {
      console.error('Failed to fetch management entity funds:', err);
      setManagementFunds([]);
    } finally {
      setLoadingManagementFunds(false);
    }
  };

  const handleCloseManagementModal = () => {
    setManagementModalOpen(false);
    setManagementFunds([]);
    setSelectedMgmtEntity(null);
  };

  const handleViewFund = (fundId) => {
    handleCloseManagementModal();
    navigate(`/fund/${fundId}`);
  };

  const handleDepthChange = (event) => {
    setHierarchyDepth(event.target.value);
  };

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
        <Button startIcon={<BackIcon />} onClick={() => navigate('/')} sx={{ mt: 2 }}>
          Back to Search
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link underline="hover" color="inherit" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          Home
        </Link>
        <Typography color="text.primary">Fund Hierarchy Visualization</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">
          {fund?.fund_name} - Hierarchy Visualization
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Hierarchy Depth</InputLabel>
            <Select value={hierarchyDepth} label="Hierarchy Depth" onChange={handleDepthChange}>
              <MenuItem value={1}>1 Level</MenuItem>
              <MenuItem value={2}>2 Levels</MenuItem>
              <MenuItem value={3}>3 Levels</MenuItem>
            </Select>
          </FormControl>
          <Button startIcon={<RefreshIcon />} variant="outlined" onClick={fetchHierarchy}>
            Refresh
          </Button>
          <Button startIcon={<InfoIcon />} onClick={() => navigate(`/fund/${fundId}`)}>
            Details
          </Button>
          <Button startIcon={<BackIcon />} onClick={() => navigate('/')}>
            Back
          </Button>
        </Box>
      </Box>

      {/* Legend */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <Chip label="Fund" sx={{ bgcolor: '#1976d2', color: 'white' }} size="small" />
        <Chip label="Management Entity" sx={{ bgcolor: '#4caf50', color: 'white' }} size="small" />
        <Chip label="Share Class" sx={{ bgcolor: '#ff9800', color: 'white' }} size="small" />
        <Chip label="SubFund" sx={{ bgcolor: '#9c27b0', color: 'white' }} size="small" />
      </Box>

      {/* Visualization */}
      <Paper sx={{ height: '600px', mb: 2 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls />
          <MiniMap nodeColor={(node) => node.style.background} />
          <Background variant="dots" gap={12} size={1} />
        </ReactFlow>
      </Paper>

      {/* Selected Node Info */}
      {selectedNode && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Selected Node Information
            </Typography>
            <Typography variant="body2">
              <strong>ID:</strong> {selectedNode.id}
            </Typography>
            <Typography variant="body2">
              <strong>Type:</strong> {selectedNode.id.startsWith('mgmt_') ? 'Management Entity' : 
                                     selectedNode.id.startsWith('SC') ? 'Share Class' :
                                     selectedNode.id.startsWith('SF') ? 'SubFund' : 'Fund'}
            </Typography>
            {selectedNode.id.startsWith('mgmt_') && (
              <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                Click on the management entity node to view all funds it manages
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {/* Management Entity Funds Modal */}
      <Dialog
        open={managementModalOpen}
        onClose={handleCloseManagementModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Funds Managed by {selectedMgmtEntity}
            </Typography>
            <IconButton onClick={handleCloseManagementModal} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {loadingManagementFunds ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : managementFunds.length === 0 ? (
            <Alert severity="info">No funds found for this management entity</Alert>
          ) : (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Total funds: {managementFunds.length}
              </Typography>
              <List>
                {managementFunds.map((fund, index) => (
                  <React.Fragment key={fund.fund_id}>
                    {index > 0 && <Divider />}
                    <ListItem
                      disablePadding
                      secondaryAction={
                        <Button
                          size="small"
                          startIcon={<VisibilityIcon />}
                          onClick={() => handleViewFund(fund.fund_id)}
                        >
                          View
                        </Button>
                      }
                    >
                      <ListItemButton>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body1">{fund.fund_name}</Typography>
                              <Chip
                                label={fund.status}
                                size="small"
                                color={fund.status === 'ACTIVE' ? 'success' : 'default'}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {fund.fund_code} | {fund.fund_type}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Currency: {fund.base_currency} | Domicile: {fund.domicile}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseManagementModal}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FundVisualization;