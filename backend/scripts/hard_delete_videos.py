#!/usr/bin/env python3
"""
Script to hard delete video analyses
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService

async def hard_delete_videos():
    """Hard delete all video analyses"""
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
        
        print(f"Found {len(analyses)} video analyses to delete:")
        for analysis in analyses:
            doc_id = analysis.get('id')
            created_at = analysis.get('created_at', 'Unknown')
            print(f"  - {doc_id} (Created: {created_at})")
        
        print("\nDeleting...")
        
        deleted_count = 0
        failed_count = 0
        
        for analysis in analyses:
            doc_id = analysis.get('id')
            if doc_id:
                success = await firebase.delete_document("coffee_beans_analyses", doc_id)
                if success:
                    deleted_count += 1
                    print(f"✓ Deleted: {doc_id}")
                else:
                    failed_count += 1
                    print(f"✗ Failed to delete: {doc_id}")
        
        print(f"\nTotal deleted: {deleted_count}")
        print(f"Failed: {failed_count}")
        
        # Verify deletion
        remaining = await firebase.query_documents(
            collection="coffee_beans_analyses",
            filters=[("is_video", "==", True)]
        )
        print(f"\nRemaining video analyses: {len(remaining)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(hard_delete_videos())