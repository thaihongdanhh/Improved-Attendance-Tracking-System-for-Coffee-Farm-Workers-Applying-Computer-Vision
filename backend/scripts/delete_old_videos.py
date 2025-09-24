#!/usr/bin/env python3
"""
Script to delete old video analyses
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService

async def delete_old_videos():
    """Delete old video analyses"""
    firebase = FirebaseService()
    
    try:
        # Get all video analyses
        analyses = await firebase.query_documents(
            collection="coffee_beans_analyses",
            filters=[("is_video", "==", True)]
        )
        
        if not analyses:
            print("No video analyses found")
            return
        
        print(f"Found {len(analyses)} video analyses")
        
        # Show all video analyses first
        print("\nVideo analyses to delete:")
        for analysis in analyses:
            doc_id = analysis.get('id')
            created_at = analysis.get('created_at', 'Unknown')
            user_id = analysis.get('user_id', 'Unknown')
            print(f"  - ID: {doc_id}")
            print(f"    Created: {created_at}")
            print(f"    User: {user_id}")
        
        # Auto confirm deletion
        print("\nProceeding to delete all video analyses...")
        
        deleted_count = 0
        
        for analysis in analyses:
            doc_id = analysis.get('id')
            if doc_id:
                try:
                    # Delete from Firestore
                    await firebase.delete_document("coffee_beans_analyses", doc_id)
                    deleted_count += 1
                    print(f"Deleted: {doc_id}")
                except Exception as e:
                    print(f"Error deleting {doc_id}: {e}")
        
        print(f"\nTotal documents deleted: {deleted_count}")
        
    except Exception as e:
        print(f"Error: {e}")

async def delete_document(firebase, collection, doc_id):
    """Helper function to delete a document"""
    # Since FirebaseService doesn't have delete_document, we'll set it to empty
    # or you can implement actual deletion
    try:
        # Get the collection reference
        if firebase.use_real_firebase:
            doc_ref = firebase.db.collection(collection).document(doc_id)
            doc_ref.delete()
        else:
            # For mock mode, remove from mock data
            if collection in firebase._mock_data and doc_id in firebase._mock_data[collection]:
                del firebase._mock_data[collection][doc_id]
        print(f"Deleted {doc_id}")
    except Exception as e:
        print(f"Error deleting {doc_id}: {e}")

# Monkey patch the delete method
from app.services.firebase_service import FirebaseService
FirebaseService.delete_document = delete_document

if __name__ == "__main__":
    asyncio.run(delete_old_videos())