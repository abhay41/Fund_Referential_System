import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Fund API endpoints
export const fundAPI = {
  // Search funds with filters and pagination
  searchFunds: (params) => {
    return api.get('/funds/search', { params });
  },

  // Get fund by code
  getFundByCode: (fundCode) => {
    return api.get(`/funds/code/${fundCode}`);
  },

  // Get fund by ID
  getFundById: (fundId) => {
    return api.get(`/funds/${fundId}`);
  },

  // Get fund hierarchy (children)
  getFundHierarchyChildren: (fundId, depth = 1) => {
    return api.get(`/funds/${fundId}/hierarchy/children`, {
      params: { depth },
    });
  },

  // Get fund hierarchy (parents)
  getFundHierarchyParents: (identifier, depth = 1) => {
    return api.get(`/funds/${identifier}/hierarchy/parents`, {
      params: { depth },
    });
  },

  // Get funds by management entity
  getFundsByManagementEntity: (mgmtId, page = 1, pageSize = 10) => {
    return api.get(`/management/${mgmtId}/funds`, {
      params: { page, page_size: pageSize },
    });
  },

  // Create new fund
  createFund: (fundData) => {
    return api.post('/funds/', fundData);
  },

  // Update fund
  updateFund: (fundId, updateData) => {
    return api.put(`/funds/${fundId}`, updateData);
  },
};

// Management Entity API endpoints
export const managementAPI = {
  // Get management entity by ID
  getManagementEntityById: (mgmtId) => {
    return api.get(`/management/${mgmtId}`);
  },

  // List all management entities
  getAllManagementEntities: (page = 1, pageSize = 10) => {
    return api.get('/management/', {
      params: { skip: (page - 1) * pageSize, limit: pageSize },
    });
  },

  // Search management entities
  searchManagementEntities: (params) => {
    return api.get('/management/search', { params });
  },

  // Get funds by management entity
  getManagementEntityFunds: (mgmtId, page = 1, pageSize = 10) => {
    return api.get(`/management/${mgmtId}/funds`, {
      params: { page, page_size: pageSize },
    });
  },
};

// SubFund API endpoints
export const subfundAPI = {
  // Get subfund by ID
  getSubFundById: (subfundId) => {
    return api.get(`/subfunds/${subfundId}`);
  },

  // List all subfunds
  getAllSubFunds: (page = 1, pageSize = 10) => {
    return api.get('/subfunds/', {
      params: { skip: (page - 1) * pageSize, limit: pageSize },
    });
  },

  // Search subfunds
  searchSubFunds: (params) => {
    return api.get('/subfunds/search', { params });
  },

  // Get subfund children
  getSubFundChildren: (subfundId) => {
    return api.get(`/subfunds/${subfundId}/children`);
  },

  // Get subfund full hierarchy
  getSubFundHierarchy: (subfundId, depth = 3) => {
    return api.get(`/subfunds/${subfundId}/hierarchy`, {
      params: { depth },
    });
  },
};

// Share Class API endpoints
export const shareClassAPI = {
  // Get share class by ID
  getShareClassById: (scId) => {
    return api.get(`/share-classes/${scId}`);
  },

  // List all share classes
  getAllShareClasses: (page = 1, pageSize = 10) => {
    return api.get('/share-classes/', {
      params: { skip: (page - 1) * pageSize, limit: pageSize },
    });
  },

  // Search share classes
  searchShareClasses: (params) => {
    return api.get('/share-classes/search', { params });
  },
};

// Legal Entity API endpoints
export const legalEntityAPI = {
  // Get legal entity by ID
  getLegalEntityById: (leId) => {
    return api.get(`/legal-entities/${leId}`);
  },

  // List all legal entities
  getAllLegalEntities: (page = 1, pageSize = 10) => {
    return api.get('/legal-entities/', {
      params: { skip: (page - 1) * pageSize, limit: pageSize },
    });
  },

  // Search legal entities
  searchLegalEntities: (params) => {
    return api.get('/legal-entities/search', { params });
  },
};

// Statistics API endpoints
export const statisticsAPI = {
  // Get fund statistics
  getFundStatistics: () => {
    return api.get('/statistics/funds');
  },

  // Get management entity statistics
  getManagementStatistics: () => {
    return api.get('/statistics/management');
  },

  // Get all dashboard statistics (combined)
  getDashboardStatistics: () => {
    return api.get('/statistics/dashboard');
  },
};

export default api;
