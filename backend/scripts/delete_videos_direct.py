#!/usr/bin/env python3
"""
Script to delete video analyses directly from Firestore
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import firestore
from app.core.config import settings
import json

async def delete_videos_direct():
    """Delete video analyses directly"""
    
    # Initialize Firestore client
    if os.path.exists(settings.FIREBASE_CONFIG_PATH):
        with open(settings.FIREBASE_CONFIG_PATH) as f:
            credentials = json.load(f)
        
        project_id = credentials.get('project_id')
        db = firestore.Client(project=project_id)
        
        # Get all video analyses
        collection_ref = db.collection("coffee_beans_analyses")
        query = collection_ref.where("is_video", "==", True)
        docs = query.get()
        
        print(f"Found {len(docs)} video analyses to delete")
        
        deleted_count = 0
        for doc in docs:
            doc_data = doc.to_dict()
            print(f"Deleting: {doc.id} - Created: {doc_data.get('created_at', 'Unknown')}")
            
            # Delete the document
            doc.reference.delete()
            deleted_count += 1
        
        print(f"\nTotal documents deleted: {deleted_count}")
        
        # Verify deletion
        remaining_docs = query.get()
        print(f"Remaining video analyses: {len(remaining_docs)}")
        
    else:
        print(f"Firebase credentials not found at {settings.FIREBASE_CONFIG_PATH}")

if __name__ == "__main__":
    asyncio.run(delete_videos_direct())