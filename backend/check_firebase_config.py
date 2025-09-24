#!/usr/bin/env python3
import os
import sys

# Check environment variables
print("=== Checking Environment Variables ===")
print(f"Current working directory: {os.getcwd()}")

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Check config
print(f"\nUSE_MOCK_FIREBASE env: {os.getenv('USE_MOCK_FIREBASE')}")
print(f"FIREBASE_CONFIG_PATH env: {os.getenv('FIREBASE_CONFIG_PATH')}")

# Import settings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.config import settings

print(f"\n=== Settings Object ===")
print(f"USE_MOCK_FIREBASE: {settings.USE_MOCK_FIREBASE}")
print(f"FIREBASE_CONFIG_PATH: {settings.FIREBASE_CONFIG_PATH}")

# Check if Firebase config file exists
if settings.FIREBASE_CONFIG_PATH:
    full_path = os.path.abspath(settings.FIREBASE_CONFIG_PATH)
    print(f"\nChecking Firebase config file: {full_path}")
    print(f"File exists: {os.path.exists(full_path)}")
    
    if os.path.exists(full_path):
        import json
        with open(full_path, 'r') as f:
            config = json.load(f)
            print(f"Project ID: {config.get('project_id')}")
else:
    print("\nNo Firebase config path set!")

# Test Firebase initialization
print("\n=== Testing Firebase Service ===")
from app.services.firebase_service import FirebaseService

firebase = FirebaseService()
print(f"Firebase DB client: {firebase.db}")
print(f"Firebase bucket: {firebase.bucket}")
print(f"Has mock data: {hasattr(firebase, '_mock_data')}")

if hasattr(firebase, '_mock_data'):
    print("\n⚠️  WARNING: Still using MOCK mode!")
    print("Collections in mock:")
    for collection in firebase._mock_data.keys():
        print(f"  - {collection}: {len(firebase._mock_data[collection])} docs")
else:
    print("\n✅ Using REAL Firebase!")