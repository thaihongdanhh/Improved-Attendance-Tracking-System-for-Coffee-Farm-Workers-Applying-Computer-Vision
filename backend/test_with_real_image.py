#!/usr/bin/env python3
import requests
import os

# API configuration
BASE_URL = "http://sarm.n2nai.io:5200"
ANALYZE_URL = f"{BASE_URL}/api/v1/coffee-beans/analyze"
HISTORY_URL = f"{BASE_URL}/api/v1/coffee-beans/history"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl8xIiwiZW1haWwiOiJhZG1pbkBhaWNvZmZlZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDk1MzE5MzN9.OXgZHcSW5-5w0KzpxaAXRfXCNwSFbYWq8rKSbrQuWGE"

# Use an existing analyzed image
image_path = "/home/data2/AIFace/AICoffeePortal/backend/uploads/beans/beans_analysis_20250610_114904.jpg"

if os.path.exists(image_path):
    print(f"Using existing image: {image_path}")
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    with open(image_path, 'rb') as f:
        files = {
            "file": ("coffee_beans.jpg", f, "image/jpeg")
        }
        
        data = {
            "farm_id": "farm_1",
            "field_id": "field_1",
            "notes": "Test with real coffee beans image"
        }
        
        print("Sending analyze request...")
        response = requests.post(ANALYZE_URL, headers=headers, files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Analysis successful!")
            print(f"ID: {result.get('id')}")
            print(f"Quality Score: {result.get('analysis', {}).get('quality_score')}")
            print(f"Total Beans: {result.get('analysis', {}).get('total_beans')}")
            
            # Check history
            print("\nChecking history...")
            history_response = requests.get(HISTORY_URL, headers=headers)
            if history_response.status_code == 200:
                history = history_response.json()
                print(f"History has {len(history)} records")
                
                if len(history) > 0:
                    print("✅ SUCCESS: Data is being saved to Firebase!")
                else:
                    print("❌ History is still empty")
        else:
            print(f"Response: {response.text}")
else:
    print(f"Image not found: {image_path}")