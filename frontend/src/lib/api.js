import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${API_URL}/api`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Products
export const getProducts = (params) => api.get('/products', { params });
export const getTopProducts = (limit = 5) => api.get('/products/top', { params: { limit } });
export const getProduct = (id) => api.get(`/products/${id}`);
export const getProductBrief = (id) => api.get(`/products/${id}/brief`);

// Launch Kits
export const generateLaunchKit = (productId) => api.post(`/launch-kit/${productId}`);
export const getLaunchKits = () => api.get('/launch-kits');
export const getLaunchKit = (id) => api.get(`/launch-kit/${id}`);

// Reports
export const getDailyReport = () => api.get('/reports/daily');

// Boards
export const createBoard = (name, description) => api.post('/boards', null, { params: { name, description } });
export const getBoards = () => api.get('/boards');
export const addProductToBoard = (boardId, productId) => api.post(`/boards/${boardId}/products/${productId}`);
export const removeProductFromBoard = (boardId, productId) => api.delete(`/boards/${boardId}/products/${productId}`);

// Settings
export const getFilterSettings = () => api.get('/settings/filters');
export const updateFilterSettings = (filters) => api.put('/settings/filters', filters);

// Categories & Stats
export const getCategories = () => api.get('/categories');
export const getStats = () => api.get('/stats');

// Seed data
export const seedData = () => api.post('/seed');

// Scanners
export const runFullScan = () => api.post('/scan/full');
export const scanSource = (source) => api.get(`/scan/sources/${source}`);
export const analyzeProduct = (productName) => api.post(`/scan/analyze/${productName}`);

// Competitors
export const addCompetitor = (storeUrl) => api.post('/competitors', null, { params: { store_url: storeUrl } });
export const getCompetitors = () => api.get('/competitors');
export const getCompetitor = (id) => api.get(`/competitors/${id}`);
export const scanCompetitor = (id) => api.post(`/competitors/${id}/scan`);
export const removeCompetitor = (id) => api.delete(`/competitors/${id}`);
export const getCompetitorAlerts = () => api.get('/competitors/alerts/all');
export const markAlertRead = (id) => api.put(`/competitors/alerts/${id}/read`);

// Saturation
export const getSaturationOverview = () => api.get('/saturation/overview');
export const getNicheSaturation = () => api.get('/saturation/niches');

// Health
export const healthCheck = () => api.get('/health');

export default api;
