#!/usr/bin/env python3
import asyncio
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService
from app.services.coffee_beans_service import CoffeeBeansService

async def test_firebase_mock():
    # Test Firebase mock data
    firebase = FirebaseService()
    coffee_service = CoffeeBeansService()
    
    print("=== Testing Firebase Mock Mode ===")
    from app.core.config import settings
    print(f"Mock mode enabled: {settings.USE_MOCK_FIREBASE}")
    
    # Check current mock data
    print("\nCurrent mock data collections:")
    for collection_name in firebase._mock_data.keys():
        collection_data = firebase._mock_data[collection_name]
        print(f"- {collection_name}: {len(collection_data)} documents")
        if collection_name == "coffee_beans_analyses":
            for doc_id, doc in collection_data.items():
                print(f"  - {doc_id}: user_id={doc.get('user_id')}, farm_id={doc.get('farm_id')}")
    
    # Test save and retrieve
    print("\n=== Testing Save and Retrieve ===")
    test_data = {
        "user_id": "test_user",
        "farm_id": "test_farm",
        "analysis": {"quality_score": 85.5}
    }
    
    # Save
    saved = await coffee_service.save_analysis(test_data)
    print(f"Saved analysis: {saved['id']}")
    
    # Retrieve
    history = await coffee_service.get_user_history("test_user")
    print(f"History for test_user: {len(history)} records")
    
    # Check all analyses
    all_analyses = await firebase.query_documents("coffee_beans_analyses", [])
    print(f"\nTotal analyses in 'coffee_beans_analyses': {len(all_analyses)}")
    for analysis in all_analyses:
        print(f"- {analysis.get('id')}: user={analysis.get('user_id')}, created={analysis.get('created_at')}")
    
    # Check mock data directly
    print("\n=== Direct Mock Data Check ===")
    if "coffee_beans_analyses" in firebase._mock_data:
        print(f"coffee_beans_analyses collection: {len(firebase._mock_data['coffee_beans_analyses'])} docs")
        for doc_id, doc in firebase._mock_data['coffee_beans_analyses'].items():
            print(f"  - {doc_id}")
    else:
        print("coffee_beans_analyses collection not found in mock data")

if __name__ == "__main__":
    asyncio.run(test_firebase_mock())