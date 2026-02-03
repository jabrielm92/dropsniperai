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
export const getScanStatus = () => api.get('/scan/status');

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

// AI Browser Scanner
export const runAiBrowserScan = () => api.post('/scan/ai-browser/full');
export const runAiBrowserSourceScan = (source) => api.post(`/scan/ai-browser/${source}`);
export const scanCompetitorWithAi = (storeUrl) => api.post('/scan/ai-browser/competitor', null, { params: { store_url: storeUrl } });
export const scanMetaAdsWithAi = (productName) => api.post('/scan/ai-browser/meta-ads', null, { params: { product_name: productName } });
export const getAiBrowserStatus = () => api.get('/scan/ai-browser/status');

// Telegram
export const getTelegramStatus = () => api.get('/telegram/status');
export const testTelegram = () => api.post('/telegram/test');
export const sendTelegramReport = () => api.post('/telegram/send-report');
export const sendLaunchKitTelegram = (kitId) => api.post(`/telegram/send-launch-kit/${kitId}`);

// User Keys Management
export const getUserKeys = () => api.get('/user/keys');
export const updateUserKeys = (keys) => api.put('/user/keys', keys);
export const deleteUserKey = (keyType) => api.delete(`/user/keys/${keyType}`);
export const getTierStatus = () => api.get('/user/tier-status');

// Integration Status
export const getIntegrationsStatus = () => api.get('/integrations/status');

// Admin (requires admin role)
export const getAdminStats = () => api.get('/admin/stats');
export const getAdminUsers = (skip = 0, limit = 50) => api.get('/admin/users', { params: { skip, limit } });
export const getAdminUserDetail = (userId) => api.get(`/admin/users/${userId}`);
export const updateUserTier = (userId, tier) => api.put(`/admin/users/${userId}/tier`, null, { params: { tier } });
export const getRecentActivity = (limit = 20) => api.get('/admin/activity', { params: { limit } });

// Google Trends
export const getRisingTrends = (geo = 'US') => api.get('/trends/rising', { params: { geo } });
export const getKeywordInterest = (keyword, timeframe = 'today 3-m', geo = 'US') => 
  api.get(`/trends/interest/${keyword}`, { params: { timeframe, geo } });
export const getRelatedQueries = (keyword, geo = 'US') => 
  api.get(`/trends/related/${keyword}`, { params: { geo } });
export const analyzeProductsTrends = (productNames, geo = 'US') => 
  api.post('/trends/analyze-products', { product_names: productNames, geo });

// Export to E-commerce
export const exportToShopify = (config) => api.post('/export/shopify', config);
export const exportToWooCommerce = (config) => api.post('/export/woocommerce', config);
export const getExportHistory = () => api.get('/export/history');
export const downloadExport = (format, config) => api.post(`/export/download/${format}`, config);

// Payments
export const createCheckoutSession = (tier, successUrl, cancelUrl) => 
  api.post('/payments/create-checkout', { tier, success_url: successUrl, cancel_url: cancelUrl });
export const getSubscriptionStatus = () => api.get('/payments/subscription');
export const createPortalSession = () => api.post('/payments/portal');

// Health
export const healthCheck = () => api.get('/health');

export default api;
