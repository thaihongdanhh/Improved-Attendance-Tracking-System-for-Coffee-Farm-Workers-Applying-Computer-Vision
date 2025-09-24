#!/usr/bin/env python3
import requests
import json
import base64
from datetime import datetime

# API configuration
BASE_URL = "http://sarm.n2nai.io:5200"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ANALYZE_URL = f"{BASE_URL}/api/v1/coffee-beans/analyze"
HISTORY_URL = f"{BASE_URL}/api/v1/coffee-beans/history"

# Test credentials
USERNAME = "admin@aicoffee.com"
PASSWORD = "admin123"

def login():
    """Login and get access token"""
    print(f"\n=== Login as {USERNAME} ===")
    
    # FastAPI expects form data for login
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(LOGIN_URL, data=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Login successful! Token type: {result['token_type']}")
        return result['access_token']
    else:
        print(f"Login failed: {response.text}")
        return None

def test_analyze(token):
    """Test coffee beans analyze endpoint"""
    print("\n=== Testing Analyze Endpoint ===")
    
    # Create a simple test image (1x1 pixel red image)
    # In real usage, this would be an actual coffee beans image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        "file": ("test_beans.jpg", img_bytes, "image/jpeg")
    }
    
    data = {
        "user_id": "admin_1",
        "farm_id": "farm_1",
        "field_id": "field_1"
    }
    
    response = requests.post(ANALYZE_URL, headers=headers, files=files, data=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Analysis successful!")
        print(f"Analysis ID: {result.get('id', 'N/A')}")
        print(f"Quality Score: {result.get('analysis', {}).get('quality_score', 'N/A')}")
        print(f"Total Beans: {result.get('analysis', {}).get('total_beans', 'N/A')}")
        return result
    else:
        print(f"Analysis failed: {response.text}")
        return None

def test_history(token):
    """Test coffee beans history endpoint"""
    print("\n=== Testing History Endpoint ===")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(HISTORY_URL, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"Found {len(results)} analysis records")
        
        for i, record in enumerate(results[:3]):  # Show first 3 records
            print(f"\nRecord {i+1}:")
            print(f"  ID: {record.get('id', 'N/A')}")
            print(f"  User ID: {record.get('user_id', 'N/A')}")
            print(f"  Farm ID: {record.get('farm_id', 'N/A')}")
            print(f"  Created: {record.get('created_at', 'N/A')}")
            if 'analysis' in record:
                print(f"  Quality Score: {record['analysis'].get('quality_score', 'N/A')}")
        
        return results
    else:
        print(f"History failed: {response.text}")
        return None

def main():
    """Main test flow"""
    print("=== Coffee Beans API Test ===")
    print(f"Testing server: {BASE_URL}")
    
    # Step 1: Login
    token = login()
    if not token:
        print("Failed to login. Exiting.")
        return
    
    # Step 2: Test analyze endpoint
    print("\nWaiting 1 second...")
    import time
    time.sleep(1)
    
    analysis_result = test_analyze(token)
    
    # Step 3: Test history endpoint
    print("\nWaiting 1 second...")
    time.sleep(1)
    
    history_results = test_history(token)
    
    # Summary
    print("\n=== Test Summary ===")
    if analysis_result and history_results:
        # Check if our analysis appears in history
        analysis_id = analysis_result.get('id')
        found_in_history = any(r.get('id') == analysis_id for r in history_results)
        
        if found_in_history:
            print("✅ SUCCESS: Analysis was saved and appears in history!")
        else:
            print("❌ ISSUE: Analysis was not found in history")
            print(f"   Analysis ID: {analysis_id}")
            print(f"   History IDs: {[r.get('id') for r in history_results[:5]]}")
    else:
        print("❌ FAILED: Could not complete tests")

if __name__ == "__main__":
    # Check if PIL is available
    try:
        from PIL import Image
        main()
    except ImportError:
        print("Please install Pillow: pip install Pillow")
        print("Creating simpler test without image generation...")
        
        # Simplified version without PIL
        token = login()
        if token:
            print("\nTesting history endpoint only...")
            test_history(token)