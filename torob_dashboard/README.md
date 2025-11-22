# Torob Market Geographical Dashboard

## Overview
This is a comprehensive geographical dashboard for analyzing Torob market data. It provides interactive visualizations of shop distributions across Iranian cities and provinces.

## Architecture
- **Backend**: FastAPI (Python) - RESTful API for data processing
- **Frontend**: React.js - Interactive dashboard with maps and charts
- **Data**: CSV files containing shop, product, and geographical information

## Features

### 🗺️ Interactive Map
- Geographic visualization of shop distributions
- Circle markers sized by shop count
- Click for detailed city information

### 📊 Analytics Dashboard
- Total shops, cities, and provinces metrics
- Shop type distribution (online, offline, mixed)
- Top cities by shop count
- Detailed charts and visualizations

### 🔍 Data API
- RESTful endpoints for data access
- Real-time analytics
- Search and filtering capabilities

## Data Structure

### Shop Data (`torob_shops.csv`)
- **165,002 shops** with basic information
- Fields: id, name, domain, city, shop_type, etc.

### Shop Details (`shopinfo_detail.csv`)
- Detailed shop information including provinces
- Contact information and addresses
- Business details and verification status

### Product Data (`shop_products.csv`)
- Product listings with categories and prices
- Shop-product relationships
- Market analysis data

## Quick Start

### Method 1: Using the Startup Script
```bash
cd /home/maede/Projects/torob_analysis/torob_dashboard
./start.sh
```

### Method 2: Manual Setup

#### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## API Endpoints

### Health & Status
- `GET /api/health` - System health check
- `GET /api/analytics/overview` - Overall statistics

### Shop Data
- `GET /api/shops/by-city` - Shops grouped by city
- `GET /api/shops/by-province` - Shops grouped by province
- `GET /api/shops/top-cities` - Top cities by shop count
- `GET /api/shops/search` - Search shops with filters

### Map Data
- `GET /api/maps/geojson` - GeoJSON data for map visualization

## Usage Examples

### API Testing
```bash
# Check system health
curl http://localhost:8000/api/health

# Get analytics overview
curl http://localhost:8000/api/analytics/overview

# Get top 10 cities
curl http://localhost:8000/api/shops/top-cities?limit=10

# Search for online shops in Tehran
curl "http://localhost:8000/api/shops/search?city=تهران&shop_type=online"
```

### Frontend Access
- Dashboard: http://localhost:3000
- Interactive maps and charts
- Persian language support (RTL)

## Technical Details

### Backend Technology Stack
- **FastAPI**: Modern Python web framework
- **Pandas**: Data processing and analysis
- **Uvicorn**: ASGI server for high performance
- **Pydantic**: Data validation and serialization

### Frontend Technology Stack
- **React 18**: Component-based UI framework
- **Material-UI**: Professional React components
- **React-Leaflet**: Interactive maps
- **Recharts**: Data visualization charts
- **Axios**: HTTP client for API communication

### Data Processing
- Efficient CSV data loading and caching
- Real-time aggregation and filtering
- Geographic coordinate mapping for visualization
- Persian text support with proper fonts

## File Structure
```
torob_dashboard/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html       # HTML template
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── App.js           # Main application
│   └── package.json         # Node.js dependencies
├── start.sh                 # Startup script
└── README.md               # This file
```

## Key Components

### MapComponent
- Interactive Leaflet map
- Geographic visualization
- City markers with shop counts

### ChartsComponent
- Bar charts for city comparisons
- Pie charts for distribution analysis
- Responsive design

### MetricsCards
- Key performance indicators
- Colorful metric displays
- Real-time data updates

## Data Insights

Based on the loaded data:
- **165,000+** shops across Iran
- Coverage of major Iranian cities
- Mix of online, offline, and hybrid shops
- Comprehensive product categorization

## Performance Considerations
- Efficient data loading strategies
- Pagination for large datasets
- Client-side caching
- Optimized API responses

## Development Notes
- Persian/Farsi language support (RTL)
- Responsive design for mobile devices
- Error handling and loading states
- Professional UI/UX design

## Future Enhancements
- Real-time data updates
- Advanced filtering options
- Export functionality
- Mobile application
- Enhanced geographical features

---
*Created for comprehensive market analysis of Torob e-commerce data*
