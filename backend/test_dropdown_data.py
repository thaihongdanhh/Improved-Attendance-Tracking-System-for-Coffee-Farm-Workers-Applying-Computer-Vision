#!/usr/bin/env python3
"""
Test dropdown data for frontend
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5200/api/v1"
USERNAME = "admin@aicoffee.com"
PASSWORD = "admin123"

def login():
    """Login and get token"""
    print("Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_data_structure(token):
    """Test data structure for dropdowns"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*50)
    print("FARMS DATA STRUCTURE")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/farms/", headers=headers)
    if response.status_code == 200:
        farms = response.json()
        print(f"Found {len(farms)} farms")
        if farms:
            print("\nFirst farm structure:")
            print(json.dumps(farms[0], indent=2))
            
            print("\nAll farm names:")
            for farm in farms:
                print(f"- {farm.get('name', 'NO NAME')} (id: {farm.get('id', 'NO ID')})")
    else:
        print(f"❌ Farms request failed: {response.status_code}")
    
    print("\n" + "="*50)
    print("FARMERS DATA STRUCTURE") 
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/farmers/", headers=headers)
    if response.status_code == 200:
        farmers = response.json()
        print(f"Found {len(farmers)} farmers")
        if farmers:
            print("\nFirst farmer structure:")
            print(json.dumps(farmers[0], indent=2))
            
            print("\nFarmers with farm associations:")
            for farmer in farmers[:10]:  # Show first 10
                name = farmer.get('full_name', farmer.get('name', 'NO NAME'))
                farm_id = farmer.get('farm_id', 'NO FARM_ID')
                farmer_code = farmer.get('farmer_code', farmer.get('id', 'NO CODE'))
                print(f"- {name} (farm_id: {farm_id}, code: {farmer_code})")
    else:
        print(f"❌ Farmers request failed: {response.status_code}")

if __name__ == "__main__":
    print("🔍 Testing dropdown data structure...")
    
    # Login
    token = login()
    if not token:
        exit(1)
    
    # Test data structure
    test_data_structure(token)