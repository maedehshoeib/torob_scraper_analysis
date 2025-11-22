import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Paper, Typography, Box } from '@mui/material';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ChartsComponent = ({ cityData, shopTypeData, loading }) => {
  if (loading) {
    return (
      <Box className="loading">
        <Typography>در حال بارگذاری نمودارها...</Typography>
      </Box>
    );
  }

  // Prepare data for top cities chart
  const topCitiesData = cityData ? cityData.slice(0, 10).map(city => ({
    name: city.city,
    shops: city.shop_count,
    online: city.online_shops,
    offline: city.offline_shops,
    mixed: city.mixed_shops
  })) : [];

  // Prepare shop type distribution data
  const shopTypeChartData = shopTypeData ? Object.entries(shopTypeData).map(([type, count]) => ({
    name: type === 'online' ? 'آنلاین' : type === 'offline' ? 'آفلاین' : type === 'online-offline' ? 'ترکیبی' : type,
    value: count,
    count: count
  })) : [];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Top Cities Bar Chart */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          ده شهر برتر از نظر تعداد فروشگاه
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={topCitiesData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 12 }}
              interval={0}
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                value.toLocaleString('fa-IR'), 
                name === 'shops' ? 'تعداد فروشگاه' : 
                name === 'online' ? 'آنلاین' :
                name === 'offline' ? 'آفلاین' : 'ترکیبی'
              ]}
              labelFormatter={(label) => `شهر: ${label}`}
            />
            <Bar dataKey="shops" fill="#1976d2" name="shops" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Shop Type Distribution Pie Chart */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          توزیع انواع فروشگاه
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={shopTypeChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {shopTypeChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value) => [value.toLocaleString('fa-IR'), 'تعداد']}
            />
          </PieChart>
        </ResponsiveContainer>
      </Paper>

      {/* Detailed Shop Types Bar Chart */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          توزیع تفصیلی انواع فروشگاه در شهرهای برتر
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={topCitiesData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 12 }}
              interval={0}
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                value.toLocaleString('fa-IR'), 
                name === 'online' ? 'آنلاین' :
                name === 'offline' ? 'آفلاین' : 'ترکیبی'
              ]}
              labelFormatter={(label) => `شهر: ${label}`}
            />
            <Bar dataKey="online" stackId="a" fill="#0088FE" name="online" />
            <Bar dataKey="offline" stackId="a" fill="#00C49F" name="offline" />
            <Bar dataKey="mixed" stackId="a" fill="#FFBB28" name="mixed" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  );
};

export default ChartsComponent;
