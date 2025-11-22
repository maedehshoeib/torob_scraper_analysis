#!/usr/bin/env python3
"""
Demo script showing key features of the Torob Dashboard
"""

import pandas as pd
import os

def analyze_data():
    """Analyze the Torob data to show dashboard capabilities"""
    
    print("🔍 Torob Market Data Analysis")
    print("=" * 50)
    
    base_path = "/home/maede/Projects/torob_analysis"
    
    # Load shop data
    print("📊 Loading shop data...")
    try:
        shops_df = pd.read_csv(f"{base_path}/torob_shops.csv")
        print(f"✅ Loaded {len(shops_df):,} shops")
        
        # Basic statistics
        print("\n📈 Basic Statistics:")
        print(f"   • Total shops: {len(shops_df):,}")
        print(f"   • Unique cities: {shops_df['city'].nunique():,}")
        print(f"   • Shop types: {shops_df['shop_type'].nunique()}")
        
        # Top cities
        print("\n🏆 Top 10 Cities by Shop Count:")
        top_cities = shops_df['city'].value_counts().head(10)
        for i, (city, count) in enumerate(top_cities.items(), 1):
            print(f"   {i:2d}. {city}: {count:,} shops")
        
        # Shop type distribution
        print("\n🏪 Shop Type Distribution:")
        shop_types = shops_df['shop_type'].value_counts()
        for shop_type, count in shop_types.items():
            percentage = (count / len(shops_df)) * 100
            print(f"   • {shop_type}: {count:,} ({percentage:.1f}%)")
        
    except FileNotFoundError:
        print("❌ Shop data file not found")
        return
    except Exception as e:
        print(f"❌ Error loading shop data: {e}")
        return
    
    # Try to load additional data
    try:
        print("\n📋 Loading additional data...")
        
        # Shop details
        if os.path.exists(f"{base_path}/shopinfo_detail.csv"):
            # Just check the file size instead of loading the full file
            file_size = os.path.getsize(f"{base_path}/shopinfo_detail.csv") / (1024 * 1024)
            print(f"✅ Shop details file available ({file_size:.1f} MB)")
        
        # Products
        if os.path.exists(f"{base_path}/shop_products.csv"):
            try:
                products_df = pd.read_csv(f"{base_path}/shop_products.csv", nrows=1000)  # Sample first 1000 rows
                print(f"✅ Products data available (sampled 1,000 rows)")
                print(f"   • Unique shops with products: {products_df['shop_id'].nunique():,}")
            except Exception as e:
                print(f"⚠️  Products file exists but couldn't sample: {e}")
                
    except Exception as e:
        print(f"⚠️  Error checking additional files: {e}")
    
    print("\n🌟 Dashboard Features:")
    print("   🗺️  Interactive geographical map")
    print("   📊 City and province analytics")
    print("   📈 Shop distribution charts")
    print("   🔍 Search and filtering capabilities")
    print("   📱 Responsive web interface")
    print("   🌐 RESTful API for data access")
    
    print("\n🚀 To start the dashboard:")
    print("   1. Backend:  python start_backend.py")
    print("   2. Frontend: cd frontend && npm install && npm start")
    print("   3. Visit:    http://localhost:3000")
    print("   4. API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    analyze_data()
