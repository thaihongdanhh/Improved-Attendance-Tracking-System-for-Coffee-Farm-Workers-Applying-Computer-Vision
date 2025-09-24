#!/usr/bin/env python3
import requests
import base64

# Create a simple test image (green leaf)
image_data = base64.b64decode('/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCywAH/2Q==')

# API configuration
BASE_URL = "http://sarm.n2nai.io:5200"
ANALYZE_URL = f"{BASE_URL}/api/v1/coffee-leaves/analyze"
HISTORY_URL = f"{BASE_URL}/api/v1/coffee-leaves/history"
TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl8xIiwiZW1haWwiOiJhZG1pbkBhaWNvZmZlZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDk1NjA5ODJ9.BuUNLEi74xiAA19g-woAirtcEMeakxp2RFc9PXqgGC4"

headers = {
    "Authorization": TOKEN
}

files = {
    "file": ("test_leaves.jpg", image_data, "image/jpeg")
}

data = {
    "farm_id": "farm_1",
    "field_id": "field_1",
    "notes": "Test coffee leaves analysis"
}

print("=== Testing Coffee Leaves API ===")
print("\n1. Analyzing leaf image...")
response = requests.post(ANALYZE_URL, headers=headers, files=files, data=data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Analysis successful!")
    print(f"ID: {result.get('id')}")
    print(f"Health Score: {result.get('analysis', {}).get('health_score')}%")
    print(f"Total Leaves: {result.get('analysis', {}).get('total_leaves')}")
    print(f"Infected Leaves: {result.get('analysis', {}).get('infected_leaves')}")
    
    diseases = result.get('analysis', {}).get('diseases_detected', [])
    if diseases:
        print(f"\nDiseases detected:")
        for disease in diseases:
            print(f"  - {disease['disease']} ({disease['severity']} severity, {disease['confidence']*100:.1f}% confidence)")
    
    recommendations = result.get('analysis', {}).get('recommendations', [])
    if recommendations:
        print(f"\nRecommendations:")
        for rec in recommendations[:3]:
            print(f"  - {rec}")
else:
    print(f"❌ Error: {response.text}")

print("\n2. Checking history...")
history_response = requests.get(HISTORY_URL, headers=headers)
print(f"Status: {history_response.status_code}")

if history_response.status_code == 200:
    history = history_response.json()
    print(f"\n✅ Found {len(history)} analysis records")
    
    if len(history) > 0:
        print("\nRecent analyses:")
        for record in history[:3]:
            print(f"  - {record['id']}: Health Score {record['analysis']['health_score']}%")
            if record['analysis']['diseases_detected']:
                diseases = [d['disease'] for d in record['analysis']['diseases_detected']]
                print(f"    Diseases: {', '.join(diseases)}")
else:
    print(f"❌ Error: {history_response.text}")