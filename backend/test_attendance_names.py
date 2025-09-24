#!/usr/bin/env python3
"""
Test script to verify attendance endpoint returns farmer_name and farm_name
"""
import requests
import json
from datetime import datetime

# API base URL - adjust if needed
BASE_URL = "http://localhost:8000/api/v1"

# Test credentials
USERNAME = "admin"
PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_today_attendance():
    """Test the /attendance/today endpoint"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing /attendance/today endpoint ===")
    response = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nDate: {data['date']}")
        print(f"Total records: {data['total']}")
        
        if data['attendances']:
            print("\nAttendance records:")
            for i, record in enumerate(data['attendances'][:3]):  # Show first 3 records
                print(f"\n  Record {i+1}:")
                print(f"    ID: {record.get('id', 'N/A')}")
                print(f"    Farmer ID: {record.get('farmer_id', 'N/A')}")
                print(f"    Farmer Name: {record.get('farmer_name', 'N/A')}")
                print(f"    Farm ID: {record.get('farm_id', 'N/A')}")
                print(f"    Farm Name: {record.get('farm_name', 'N/A')}")
                print(f"    Check-in: {record.get('check_in_time', 'N/A')}")
                print(f"    Status: {record.get('status', 'N/A')}")
                
                # Check if farmer_name and farm_name are present
                if 'farmer_name' not in record:
                    print("    ⚠️  WARNING: farmer_name field is missing!")
                if 'farm_name' not in record:
                    print("    ⚠️  WARNING: farm_name field is missing!")
        else:
            print("\nNo attendance records found for today.")
    else:
        print(f"\nError: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_today_attendance()