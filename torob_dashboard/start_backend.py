#!/usr/bin/env python3
"""
Simple script to start the Torob Dashboard Backend
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Torob Market Geographical Dashboard Backend...")
    
    # Change to the dashboard directory
    dashboard_dir = "/home/maede/Projects/torob_analysis/torob_dashboard"
    os.chdir(dashboard_dir)
    
    # Check if backend directory exists
    if not os.path.exists("backend/main.py"):
        print("❌ Backend main.py not found!")
        return 1
    
    print("📂 Working directory:", os.getcwd())
    print("🐍 Python version:", sys.version)
    
    # Try to import required modules
    try:
        import fastapi
        import uvicorn
        import pandas
        print("✅ All required packages are available")
        print(f"   - FastAPI: {fastapi.__version__}")
        print(f"   - Pandas: {pandas.__version__}")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "pandas", "pydantic"])
    
    # Start the server
    print("\n🌟 Starting FastAPI server...")
    print("📊 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
