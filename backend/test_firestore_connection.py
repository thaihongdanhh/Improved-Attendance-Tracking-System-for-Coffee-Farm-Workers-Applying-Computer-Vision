#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService
from app.core.config import settings

async def test_firestore():
    print("=== Testing Firestore Connection ===")
    print(f"USE_MOCK_FIREBASE: {settings.USE_MOCK_FIREBASE}")
    print(f"FIREBASE_CONFIG_PATH: {settings.FIREBASE_CONFIG_PATH}")
    
    # Create FirebaseService instance
    firebase = FirebaseService()
    
    # Check if using mock or real Firebase
    if settings.USE_MOCK_FIREBASE:
        print("\n❌ ERROR: Still using MOCK Firebase!")
        print("Mock data collections:")
        for collection in firebase._mock_data.keys():
            print(f"  - {collection}")
    else:
        print("\n✅ Using REAL Firebase")
        print(f"Firestore client: {firebase.db}")
        print(f"Storage bucket: {firebase.bucket}")
        
        # Try to create a test document
        test_data = {
            "test": True,
            "timestamp": "2025-01-10",
            "message": "Testing Firestore connection"
        }
        
        try:
            # Create test document
            await firebase.save_document("test_collection", "test_doc_1", test_data)
            print("\n✅ Successfully created test document in Firestore!")
            
            # Read it back
            retrieved = await firebase.get_document("test_collection", "test_doc_1")
            print(f"Retrieved data: {retrieved}")
            
            # Query coffee_beans_analyses collection
            print("\n=== Checking coffee_beans_analyses collection ===")
            analyses = await firebase.query_documents("coffee_beans_analyses", [])
            print(f"Found {len(analyses)} documents in coffee_beans_analyses")
            
            if len(analyses) > 0:
                print("Sample document:")
                print(f"  ID: {analyses[0].get('id')}")
                print(f"  User: {analyses[0].get('user_id')}")
                print(f"  Created: {analyses[0].get('created_at')}")
            
        except Exception as e:
            print(f"\n❌ ERROR connecting to Firestore: {e}")
            print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_firestore())