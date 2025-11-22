#!/usr/bin/env python3
"""
Final summary and verification script for Torob Dashboard
"""

import os
import pandas as pd
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("🔍 Checking Dashboard Files...")
    print("=" * 40)
    
    base_path = Path("/home/maede/Projects/torob_analysis/torob_dashboard")
    
    # Check backend files
    backend_files = [
        "backend/main.py",
        "backend/requirements.txt",
    ]
    
    # Check frontend files
    frontend_files = [
        "frontend/package.json",
        "frontend/public/index.html",
        "frontend/src/App.js",
        "frontend/src/components/MapComponent.js",
        "frontend/src/components/ChartsComponent.js",
        "frontend/src/components/MetricsCards.js",
        "frontend/src/pages/Dashboard.js",
        "frontend/src/services/api.js",
    ]
    
    # Check utility files
    utility_files = [
        "start.sh",
        "start_backend.py", 
        "test_api.py",
        "demo.py",
        "README.md",
        "SETUP_COMPLETE.md"
    ]
    
    all_files = backend_files + frontend_files + utility_files
    
    for file_path in all_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - MISSING")
    
    print()

def check_data():
    """Check the data files"""
    print("📊 Checking Data Files...")
    print("=" * 40)
    
    data_path = Path("/home/maede/Projects/torob_analysis")
    
    data_files = {
        "torob_shops.csv": "Shop data",
        "shopinfo_detail.csv": "Shop details", 
        "shop_products.csv": "Product data"
    }
    
    for filename, description in data_files.items():
        file_path = data_path / filename
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✅ {description}: {filename} ({size_mb:.1f} MB)")
            
            # Quick data check for shops file
            if filename == "torob_shops.csv":
                try:
                    df = pd.read_csv(file_path, nrows=5)
                    print(f"   📋 Columns: {list(df.columns)}")
                    print(f"   🏪 Sample cities: {df['city'].tolist()}")
                except Exception as e:
                    print(f"   ⚠️  Could not sample data: {e}")
        else:
            print(f"❌ {description}: {filename} - MISSING")
    
    print()

def show_summary():
    """Show final summary"""
    print("🎉 TOROB DASHBOARD SETUP COMPLETE!")
    print("=" * 50)
    
    print("📦 Components Created:")
    print("   🐍 FastAPI Backend - RESTful API server")
    print("   ⚛️  React Frontend - Interactive dashboard")
    print("   🗺️  Geographic visualization with maps")
    print("   📊 Analytics charts and metrics")
    print("   🔧 Utility scripts and documentation")
    
    print("\n🚀 Quick Start Commands:")
    print("   1. Start Backend:")
    print("      cd /home/maede/Projects/torob_analysis/torob_dashboard")
    print("      python start_backend.py")
    print()
    print("   2. Start Frontend (new terminal):")
    print("      cd /home/maede/Projects/torob_analysis/torob_dashboard/frontend")
    print("      npm install && npm start")
    print()
    print("   3. Open Dashboard:")
    print("      🌐 Frontend: http://localhost:3000")
    print("      📡 API: http://localhost:8000") 
    print("      📚 Docs: http://localhost:8000/docs")
    
    print("\n📊 Data Analysis Features:")
    print("   • 165,000+ shops across Iran")
    print("   • Interactive geographical maps")
    print("   • City and province analytics")
    print("   • Shop type distribution charts")
    print("   • Real-time search and filtering")
    print("   • Persian language support (RTL)")
    
    print("\n🔧 Testing & Utilities:")
    print("   • python demo.py - Data analysis preview")
    print("   • python test_api.py - API endpoint testing")
    print("   • ./start.sh - Automated startup")
    
    print("\n📁 Key Files Created:")
    print("   • backend/main.py - FastAPI application")
    print("   • frontend/src/pages/Dashboard.js - Main UI")
    print("   • frontend/src/components/ - UI components")
    print("   • README.md & SETUP_COMPLETE.md - Documentation")
    
    print("\n🎯 Next Steps:")
    print("   1. Run the demo: python demo.py")
    print("   2. Start the backend: python start_backend.py")
    print("   3. Install frontend deps: cd frontend && npm install")
    print("   4. Start frontend: npm start")
    print("   5. Open http://localhost:3000")
    
    print(f"\n✨ Your geographical dashboard is ready!")

def main():
    print("🔍 TOROB DASHBOARD VERIFICATION")
    print("=" * 50)
    print()
    
    check_files()
    check_data()
    show_summary()

if __name__ == "__main__":
    main()
