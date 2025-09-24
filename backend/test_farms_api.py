#!/usr/bin/env python3
"""
Test farms API endpoint
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

def test_farms_endpoint(token):
    """Test farms endpoint"""
    print("\nTesting /farms endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/farms", headers=headers)
    
    if response.status_code == 200:
        farms = response.json()
        print(f"✅ Found {len(farms)} farms:")
        for farm in farms:
            print(f"  - {farm['name']} ({farm['id']}) - {farm['location']}")
        return farms
    else:
        print(f"❌ Farms request failed: {response.status_code} - {response.text}")
        return []

def test_attendance_endpoint(token):
    """Test attendance endpoint"""
    print("\nTesting /attendance endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
    
    if response.status_code == 200:
        attendance = response.json()
        print(f"✅ Found attendance records (showing first 5):")
        for record in attendance[:5]:
            print(f"  - {record.get('date', 'N/A')} | {record.get('farmer_name', 'N/A')} | {record.get('farm_name', 'N/A')}")
        return attendance
    else:
        print(f"❌ Attendance request failed: {response.status_code} - {response.text}")
        return []

if __name__ == "__main__":
    print("🚀 Testing API endpoints...")
    
    # Login
    token = login()
    if not token:
        exit(1)
    
    # Test farms
    farms = test_farms_endpoint(token)
    
    # Test attendance
    attendance = test_attendance_endpoint(token)
    
    print(f"\n✅ API test completed!")
    print(f"   Farms: {len(farms)}")
    print(f"   Attendance: {len(attendance)}")