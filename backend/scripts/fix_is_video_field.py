#!/usr/bin/env python3
"""
Script to fix missing is_video field in existing coffee beans analyses
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService

async def fix_is_video_field():
    """Update existing documents to have proper is_video field"""
    firebase = FirebaseService()
    
    try:
        # Get all coffee beans analyses
        # Using query_documents to get all documents
        analyses = await firebase.query_documents(
            collection="coffee_beans_analyses",
            filters=[]
        )
        
        if not analyses:
            print("No analyses found")
            return
        
        updated_count = 0
        
        for analysis in analyses:
            doc_id = analysis.get('id')
            if not doc_id:
                continue
            
            # Check if is_video field exists
            if 'is_video' not in analysis:
                # Determine if it's a video analysis
                is_video = bool(
                    analysis.get('video_url') or 
                    analysis.get('frame_analyses') or
                    (isinstance(analysis.get('analysis'), dict) and 
                     'total_frames_analyzed' in analysis['analysis'])
                )
                
                # Update the document by saving it with the new field
                analysis['is_video'] = is_video
                await firebase.save_document(
                    "coffee_beans_analyses",
                    doc_id,
                    analysis
                )
                
                updated_count += 1
                print(f"Updated {doc_id}: is_video = {is_video}")
        
        print(f"\nTotal documents updated: {updated_count}")
        
    except Exception as e:
        print(f"Error updating documents: {e}")

if __name__ == "__main__":
    asyncio.run(fix_is_video_field())