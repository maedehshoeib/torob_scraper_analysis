from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from typing import List, Dict, Optional
from pydantic import BaseModel
import os
from collections import Counter

app = FastAPI(
    title="Torob Market Geographical Dashboard API",
    description="API for analyzing Torob market data geographically",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for data
shops_df = None
shop_details_df = None
products_df = None

def load_data():
    """Load CSV data files"""
    global shops_df, shop_details_df, products_df
    
    try:
        # Load the CSV files
        base_path = "/home/maede/Projects/torob_analysis"
        
        shops_df = pd.read_csv(f"{base_path}/torob_shops.csv")
        print(f"Loaded {len(shops_df)} shops")
        
        # Load shop details (this might be large)
        try:
            shop_details_df = pd.read_csv(f"{base_path}/shopinfo_detail.csv")
            print(f"Loaded {len(shop_details_df)} shop details")
        except Exception as e:
            print(f"Could not load shop details: {e}")
            shop_details_df = None
            
        try:
            products_df = pd.read_csv(f"{base_path}/shop_products.csv")
            print(f"Loaded {len(products_df)} products")
        except Exception as e:
            print(f"Could not load products: {e}")
            products_df = None
            
    except Exception as e:
        print(f"Error loading data: {e}")

# Load data on startup
@app.on_event("startup")
async def startup_event():
    load_data()

# Pydantic models
class ShopLocation(BaseModel):
    id: int
    name: str
    city: str
    province: Optional[str] = None
    shop_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CityStats(BaseModel):
    city: str
    province: Optional[str] = None
    shop_count: int
    online_shops: int
    offline_shops: int
    mixed_shops: int
    total_products: Optional[int] = None

class ProvinceStats(BaseModel):
    province: str
    shop_count: int
    cities: List[str]
    dominant_shop_type: str

@app.get("/")
async def root():
    return {"message": "Torob Market Geographical Dashboard API"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "shops_loaded": shops_df is not None,
        "shop_details_loaded": shop_details_df is not None,
        "products_loaded": products_df is not None,
        "total_shops": len(shops_df) if shops_df is not None else 0
    }

@app.get("/api/shops/by-city", response_model=List[CityStats])
async def get_shops_by_city():
    """Get shop statistics grouped by city"""
    if shops_df is None:
        raise HTTPException(status_code=500, detail="Shop data not loaded")
    
    # Group by city
    city_groups = shops_df.groupby('city').agg({
        'id': 'count',
        'shop_type': lambda x: (x == 'online').sum(),
        'shop_type': lambda x: (x == 'offline').sum() if 'offline' in x.values else 0,
        'shop_type': lambda x: (x == 'online-offline').sum() if 'online-offline' in x.values else 0
    }).reset_index()
    
    # Get province info if available
    province_mapping = {}
    if shop_details_df is not None:
        try:
            province_data = shop_details_df[['city', 'province']].drop_duplicates()
            province_mapping = dict(zip(province_data['city'], province_data['province']))
        except:
            pass
    
    # Process shop types properly
    result = []
    for city in shops_df['city'].unique():
        if pd.isna(city):
            continue
            
        city_data = shops_df[shops_df['city'] == city]
        shop_types = city_data['shop_type'].value_counts()
        
        result.append(CityStats(
            city=city,
            province=province_mapping.get(city),
            shop_count=len(city_data),
            online_shops=shop_types.get('online', 0),
            offline_shops=shop_types.get('offline', 0),
            mixed_shops=shop_types.get('online-offline', 0)
        ))
    
    # Sort by shop count
    result.sort(key=lambda x: x.shop_count, reverse=True)
    return result

@app.get("/api/shops/by-province", response_model=List[ProvinceStats])
async def get_shops_by_province():
    """Get shop statistics grouped by province"""
    if shop_details_df is None:
        raise HTTPException(status_code=404, detail="Shop details data not available")
    
    try:
        # Group by province
        province_groups = shop_details_df.groupby('province').agg({
            'id': 'count',
            'city': lambda x: list(set(x)),
            'shop_type': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown'
        }).reset_index()
        
        result = []
        for _, row in province_groups.iterrows():
            if pd.isna(row['province']):
                continue
                
            result.append(ProvinceStats(
                province=row['province'],
                shop_count=row['id'],
                cities=row['city'],
                dominant_shop_type=row['shop_type']
            ))
        
        # Sort by shop count
        result.sort(key=lambda x: x.shop_count, reverse=True)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing province data: {str(e)}")

@app.get("/api/shops/top-cities")
async def get_top_cities(limit: int = 20):
    """Get top cities by shop count"""
    if shops_df is None:
        raise HTTPException(status_code=500, detail="Shop data not loaded")
    
    city_counts = shops_df['city'].value_counts().head(limit)
    
    return {
        "cities": [
            {"city": city, "shop_count": int(count)} 
            for city, count in city_counts.items()
        ]
    }

@app.get("/api/shops/search")
async def search_shops(
    city: Optional[str] = None,
    province: Optional[str] = None,
    shop_type: Optional[str] = None,
    limit: int = 100
):
    """Search shops by various criteria"""
    if shops_df is None:
        raise HTTPException(status_code=500, detail="Shop data not loaded")
    
    filtered_df = shops_df.copy()
    
    if city:
        filtered_df = filtered_df[filtered_df['city'].str.contains(city, case=False, na=False)]
    
    if shop_type:
        filtered_df = filtered_df[filtered_df['shop_type'] == shop_type]
    
    # If province filter and we have shop details
    if province and shop_details_df is not None:
        try:
            province_cities = shop_details_df[
                shop_details_df['province'].str.contains(province, case=False, na=False)
            ]['city'].unique()
            filtered_df = filtered_df[filtered_df['city'].isin(province_cities)]
        except:
            pass
    
    # Limit results
    filtered_df = filtered_df.head(limit)
    
    # Convert to list of dictionaries
    result = []
    for _, row in filtered_df.iterrows():
        result.append({
            "id": int(row['id']),
            "name": row['name'],
            "city": row['city'],
            "shop_type": row['shop_type'],
            "domain": row.get('domain', ''),
            "score_percentile": row.get('score_percentile', 0)
        })
    
    return {"shops": result, "total": len(result)}

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get overall analytics overview"""
    if shops_df is None:
        raise HTTPException(status_code=500, detail="Shop data not loaded")
    
    # Basic stats
    total_shops = len(shops_df)
    unique_cities = shops_df['city'].nunique()
    shop_type_counts = shops_df['shop_type'].value_counts().to_dict()
    
    # Top cities
    top_cities = shops_df['city'].value_counts().head(10).to_dict()
    
    # Province stats if available
    province_stats = {}
    if shop_details_df is not None:
        try:
            unique_provinces = shop_details_df['province'].nunique()
            province_stats = {"unique_provinces": unique_provinces}
        except:
            pass
    
    # Product stats if available
    product_stats = {}
    if products_df is not None:
        try:
            total_products = len(products_df)
            unique_shops_with_products = products_df['shop_id'].nunique()
            product_stats = {
                "total_products": total_products,
                "unique_shops_with_products": unique_shops_with_products
            }
        except:
            pass
    
    return {
        "total_shops": total_shops,
        "unique_cities": unique_cities,
        "shop_type_distribution": shop_type_counts,
        "top_cities": top_cities,
        **province_stats,
        **product_stats
    }

@app.get("/api/maps/geojson")
async def get_geojson_data():
    """Get GeoJSON data for map visualization"""
    if shops_df is None:
        raise HTTPException(status_code=500, detail="Shop data not loaded")
    
    # For now, we'll create a simple city-based GeoJSON
    # In a real implementation, you'd have actual coordinates
    city_counts = shops_df['city'].value_counts()
    
    # Simple coordinate mapping for major Iranian cities (you should expand this)
    city_coordinates = {
        'تهران': [51.3890, 35.6892],
        'اصفهان': [51.6746, 32.6546],
        'مشهد': [59.6077, 36.2972],
        'شیراز': [52.5387, 29.5926],
        'تبریز': [46.2919, 38.0962],
        'کرج': [50.9915, 35.8327],
        'قم': [50.8764, 34.6401],
        'اهواز': [48.6693, 31.3183],
        'کرمانشاه': [47.0778, 34.3142],
        'ارومیه': [45.0761, 37.5527]
    }
    
    features = []
    for city, count in city_counts.head(50).items():  # Top 50 cities
        if city in city_coordinates:
            feature = {
                "type": "Feature",
                "properties": {
                    "city": city,
                    "shop_count": int(count),
                    "popup": f"{city}: {count} shops"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": city_coordinates[city]
                }
            }
            features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return geojson

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
