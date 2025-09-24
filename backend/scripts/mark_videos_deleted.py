#!/usr/bin/env python3
"""
Script to mark video analyses as deleted
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService

async def mark_videos_deleted():
    """Mark video analyses as deleted by adding a deleted flag"""
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
        
        deleted_count = 0
        
        for analysis in analyses:
            doc_id = analysis.get('id')
            if doc_id:
                # Add deleted flag
                analysis['deleted'] = True
                analysis['deleted_at'] = '2025-06-10T20:00:00'
                
                # Save the updated document
                await firebase.save_document(
                    "coffee_beans_analyses",
                    doc_id,
                    analysis
                )
                
                deleted_count += 1
                print(f"Marked as deleted: {doc_id}")
        
        print(f"\nTotal documents marked as deleted: {deleted_count}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(mark_videos_deleted())