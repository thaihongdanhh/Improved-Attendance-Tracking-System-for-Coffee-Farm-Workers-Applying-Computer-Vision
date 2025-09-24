#!/usr/bin/env python3
import requests
import base64

# Create a simple test image
import io

# Create a dummy image data (1x1 red pixel)
image_data = base64.b64decode('/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCywAH/2Q==')

# API configuration
BASE_URL = "http://sarm.n2nai.io:5200"
ANALYZE_URL = f"{BASE_URL}/api/v1/coffee-beans/analyze"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl8xIiwiZW1haWwiOiJhZG1pbkBhaWNvZmZlZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDk1MzE5MzN9.OXgZHcSW5-5w0KzpxaAXRfXCNwSFbYWq8rKSbrQuWGE"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

files = {
    "file": ("test_beans.jpg", image_data, "image/jpeg")
}

data = {
    "user_id": "admin_1",
    "farm_id": "farm_1", 
    "field_id": "field_1"
}

print("Sending analyze request...")
response = requests.post(ANALYZE_URL, headers=headers, files=files, data=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")