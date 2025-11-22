import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { 
  Store as StoreIcon, 
  LocationCity as CityIcon, 
  Public as PublicIcon,
  ShoppingCart as CartIcon 
} from '@mui/icons-material';

const MetricsCards = ({ analytics, loading }) => {
  if (loading) {
    return (
      <Box className="loading">
        <Typography>در حال بارگذاری آمار...</Typography>
      </Box>
    );
  }

  if (!analytics) {
    return null;
  }

  const metrics = [
    {
      title: 'تعداد کل فروشگاه‌ها',
      value: analytics.total_shops?.toLocaleString('fa-IR') || '0',
      icon: <StoreIcon sx={{ fontSize: 40 }} />,
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    },
    {
      title: 'تعداد شهرها',
      value: analytics.unique_cities?.toLocaleString('fa-IR') || '0',
      icon: <CityIcon sx={{ fontSize: 40 }} />,
      color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    },
    {
      title: 'تعداد استان‌ها',
      value: analytics.unique_provinces?.toLocaleString('fa-IR') || 'N/A',
      icon: <PublicIcon sx={{ fontSize: 40 }} />,
      color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    },
    {
      title: 'تعداد محصولات',
      value: analytics.total_products?.toLocaleString('fa-IR') || 'N/A',
      icon: <CartIcon sx={{ fontSize: 40 }} />,
      color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    },
  ];

  return (
    <Grid container spacing={3}>
      {metrics.map((metric, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              background: metric.color,
              color: 'white',
              borderRadius: 2,
              textAlign: 'center',
              height: '140px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <Box sx={{ mb: 1 }}>
              {metric.icon}
            </Box>
            <Typography variant="h4" component="div" sx={{ mb: 1, fontWeight: 'bold' }}>
              {metric.value}
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>
              {metric.title}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};

export default MetricsCards;
