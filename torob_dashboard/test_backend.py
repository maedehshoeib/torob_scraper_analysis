#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/maede/Projects/torob_analysis/torob_dashboard/backend')

try:
    from main import app, load_data
    print("✅ FastAPI app imported successfully")
    
    # Test data loading
    load_data()
    print("✅ Data loading function works")
    
    # Test a simple endpoint
    import pandas as pd
    shops_df = pd.read_csv('/home/maede/Projects/torob_analysis/torob_shops.csv')
    print(f"✅ CSV data loaded: {len(shops_df)} shops")
    
    print("\n🎉 Backend is ready to run!")
    print("To start the server, run:")
    print("cd /home/maede/Projects/torob_analysis/torob_dashboard")
    print("python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
