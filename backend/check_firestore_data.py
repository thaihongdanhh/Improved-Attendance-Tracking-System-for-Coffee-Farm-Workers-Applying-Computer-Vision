#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService
from app.core.config import settings

async def check_firestore_data():
    print("=== Checking Firestore Data ===")
    print(f"USE_MOCK_FIREBASE: {settings.USE_MOCK_FIREBASE}")
    
    firebase = FirebaseService()
    
    # Check coffee beans analyses
    print("\n=== Coffee Beans Analyses ===")
    beans_analyses = await firebase.query_documents("coffee_beans_analyses", [])
    print(f"Found {len(beans_analyses)} coffee beans analyses")
    
    if beans_analyses:
        for i, doc in enumerate(beans_analyses[:3]):
            print(f"\n{i+1}. {doc.get('id', 'No ID')}")
            print(f"   User: {doc.get('user_id', 'Unknown')}")
            print(f"   Farm: {doc.get('farm_id', 'Unknown')}")
            print(f"   Quality Score: {doc.get('analysis', {}).get('quality_score', 'N/A')}")
            print(f"   Created: {doc.get('created_at', 'Unknown')}")
    
    # Check coffee leaves analyses
    print("\n\n=== Coffee Leaves Analyses ===")
    leaves_analyses = await firebase.query_documents("coffee_leaves_analyses", [])
    print(f"Found {len(leaves_analyses)} coffee leaves analyses")
    
    if leaves_analyses:
        for i, doc in enumerate(leaves_analyses[:3]):
            print(f"\n{i+1}. {doc.get('id', 'No ID')}")
            print(f"   User: {doc.get('user_id', 'Unknown')}")
            print(f"   Farm: {doc.get('farm_id', 'Unknown')}")
            print(f"   Health Score: {doc.get('analysis', {}).get('health_score', 'N/A')}")
            print(f"   Diseases: {len(doc.get('analysis', {}).get('diseases_detected', []))} detected")
            print(f"   Created: {doc.get('created_at', 'Unknown')}")
    
    # Check if connected to real Firestore
    if not settings.USE_MOCK_FIREBASE:
        print("\n✅ Connected to REAL Firestore")
        print(f"   Project: kmou-aicofee")
    else:
        print("\n⚠️  Using MOCK mode - data is not persisted!")

if __name__ == "__main__":
    asyncio.run(check_firestore_data())