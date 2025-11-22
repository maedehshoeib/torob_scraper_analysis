#!/usr/bin/env python3
"""
Test script for the Torob Dashboard API
"""

import requests
import json
import time

def test_api_endpoint(url, description):
    """Test a single API endpoint"""
    try:
        print(f"🔍 Testing: {description}")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            
            # Print a summary of the data
            if isinstance(data, dict):
                print(f"   📊 Response keys: {list(data.keys())}")
                if 'total_shops' in data:
                    print(f"   🏪 Total shops: {data['total_shops']:,}")
                if 'unique_cities' in data:
                    print(f"   🏙️ Cities: {data['unique_cities']:,}")
            elif isinstance(data, list):
                print(f"   📋 Items count: {len(data)}")
            
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    print()

def main():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Torob Dashboard API")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print("✅ Server is responding")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the backend first:")
        print("   python start_backend.py")
        return 1
    
    # Test endpoints
    endpoints = [
        ("/api/health", "Health Check"),
        ("/api/analytics/overview", "Analytics Overview"),
        ("/api/shops/top-cities?limit=5", "Top 5 Cities"),
        ("/api/shops/by-city", "Shops by City (first 3 items)"),
        ("/api/maps/geojson", "GeoJSON Map Data"),
    ]
    
    for endpoint, description in endpoints:
        test_api_endpoint(f"{base_url}{endpoint}", description)
        time.sleep(0.5)  # Small delay between requests
    
    print("🎉 API testing complete!")
    print(f"📚 Full API documentation: {base_url}/docs")

if __name__ == "__main__":
    main()
