import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const apiService = {
  // Health check
  healthCheck: () => api.get('/api/health'),

  // Shop data endpoints
  getShopsByCity: () => api.get('/api/shops/by-city'),
  getShopsByProvince: () => api.get('/api/shops/by-province'),
  getTopCities: (limit = 20) => api.get(`/api/shops/top-cities?limit=${limit}`),
  
  // Search and filter
  searchShops: (params) => api.get('/api/shops/search', { params }),
  
  // Analytics
  getAnalyticsOverview: () => api.get('/api/analytics/overview'),
  
  // Map data
  getGeoJsonData: () => api.get('/api/maps/geojson'),
};

export default apiService;
