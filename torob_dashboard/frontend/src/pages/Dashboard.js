import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  Alert,
  CircularProgress,
  Divider 
} from '@mui/material';
import MetricsCards from '../components/MetricsCards';
import MapComponent from '../components/MapComponent';
import ChartsComponent from '../components/ChartsComponent';
import apiService from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [cityData, setCityData] = useState([]);
  const [geoData, setGeoData] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check API health first
      const healthResponse = await apiService.healthCheck();
      setHealthStatus(healthResponse.data);

      if (!healthResponse.data.shops_loaded) {
        throw new Error('داده‌های فروشگاه بارگذاری نشده است');
      }

      // Load all dashboard data in parallel
      const [
        analyticsResponse,
        cityResponse,
        geoResponse
      ] = await Promise.all([
        apiService.getAnalyticsOverview(),
        apiService.getShopsByCity(),
        apiService.getGeoJsonData()
      ]);

      setAnalytics(analyticsResponse.data);
      setCityData(cityResponse.data);
      setGeoData(geoResponse.data);

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError(err.response?.data?.detail || err.message || 'خطا در بارگذاری داده‌ها');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="60vh"
        flexDirection="column"
        gap={2}
      >
        <CircularProgress size={50} />
        <Typography variant="h6">در حال بارگذاری داشبورد...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="h6">خطا در بارگذاری داده‌ها</Typography>
          <Typography>{error}</Typography>
        </Alert>
        {healthStatus && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>وضعیت سیستم:</Typography>
            <Typography>وضعیت: {healthStatus.status}</Typography>
            <Typography>داده‌های فروشگاه: {healthStatus.shops_loaded ? 'بارگذاری شده' : 'بارگذاری نشده'}</Typography>
            <Typography>تعداد کل فروشگاه‌ها: {healthStatus.total_shops}</Typography>
          </Paper>
        )}
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        داشبورد جغرافیایی بازار ترب
      </Typography>

      {/* Health Status Alert */}
      {healthStatus && (
        <Alert severity="success" sx={{ mb: 3 }}>
          سیستم آماده است • {healthStatus.total_shops?.toLocaleString('fa-IR')} فروشگاه بارگذاری شده
        </Alert>
      )}

      {/* Metrics Cards */}
      <Box sx={{ mb: 4 }}>
        <MetricsCards analytics={analytics} loading={false} />
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* Map and Charts Grid */}
      <Grid container spacing={4}>
        {/* Map Section */}
        <Grid item xs={12} lg={6}>
          <Paper elevation={3} sx={{ p: 3, height: '580px' }}>
            <Typography variant="h6" gutterBottom>
              نقشه توزیع جغرافیایی فروشگاه‌ها
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              اندازه دایره‌ها نشان‌دهنده تعداد فروشگاه‌ها در هر شهر است
            </Typography>
            <MapComponent geoData={geoData} loading={false} />
          </Paper>
        </Grid>

        {/* Charts Section */}
        <Grid item xs={12} lg={6}>
          <ChartsComponent 
            cityData={cityData} 
            shopTypeData={analytics?.shop_type_distribution} 
            loading={false} 
          />
        </Grid>
      </Grid>

      {/* Additional Information */}
      <Box sx={{ mt: 4 }}>
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            درباره داده‌ها
          </Typography>
          <Typography variant="body2" color="text.secondary">
            این داشبورد بر اساس داده‌های فروشگاه‌های ترب ایجاد شده است و شامل اطلاعات جغرافیایی، 
            انواع فروشگاه‌ها و توزیع آن‌ها در شهرها و استان‌های مختلف ایران می‌باشد.
          </Typography>
          {analytics?.top_cities && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                شهرهای پربازده:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {Object.entries(analytics.top_cities).slice(0, 5).map(([city, count]) => 
                  `${city} (${count.toLocaleString('fa-IR')})`
                ).join(' • ')}
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default Dashboard;
