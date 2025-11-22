import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { Box, Typography } from '@mui/material';
import L from 'leaflet';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapComponent = ({ geoData, loading }) => {
  if (loading) {
    return (
      <Box className="loading">
        <Typography>در حال بارگذاری نقشه...</Typography>
      </Box>
    );
  }

  if (!geoData || !geoData.features) {
    return (
      <Box className="loading">
        <Typography>داده‌های نقشه در دسترس نیست</Typography>
      </Box>
    );
  }

  // Center on Iran
  const iranCenter = [32.4279, 53.6880];

  return (
    <MapContainer
      center={iranCenter}
      zoom={6}
      style={{ height: '500px', width: '100%', direction: 'ltr' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {geoData.features.map((feature, index) => {
        const [lng, lat] = feature.geometry.coordinates;
        const { city, shop_count } = feature.properties;
        
        // Calculate circle size based on shop count
        const radius = Math.min(Math.max(shop_count / 100, 5), 50);
        
        return (
          <CircleMarker
            key={index}
            center={[lat, lng]}
            radius={radius}
            fillColor="#1976d2"
            color="#fff"
            weight={2}
            opacity={1}
            fillOpacity={0.6}
          >
            <Popup>
              <div style={{ direction: 'rtl', textAlign: 'right' }}>
                <Typography variant="h6" component="div">
                  {city}
                </Typography>
                <Typography variant="body2">
                  تعداد فروشگاه: {shop_count.toLocaleString('fa-IR')}
                </Typography>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
};

export default MapComponent;
