#!/usr/bin/env python3
"""
Script to update user_id for existing analyses
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService

async def update_user_id():
    """Update user_id from admin_1 to 4tLQCow6fBx7gA7YIViX"""
    firebase = FirebaseService()
    
    try:
        # Get all coffee beans analyses
        analyses = await firebase.query_documents(
            collection="coffee_beans_analyses",
            filters=[]
        )
        
        if not analyses:
            print("No analyses found")
            return
        
        updated_count = 0
        target_user_id = "4tLQCow6fBx7gA7YIViX"
        
        for analysis in analyses:
            doc_id = analysis.get('id')
            current_user_id = analysis.get('user_id')
            
            if not doc_id:
                continue
            
            # Update if user_id is admin_1
            if current_user_id == 'admin_1':
                analysis['user_id'] = target_user_id
                
                # Save the updated document
                await firebase.save_document(
                    "coffee_beans_analyses",
                    doc_id,
                    analysis
                )
                
                updated_count += 1
                print(f"Updated {doc_id}: user_id = {target_user_id}")
        
        print(f"\nTotal documents updated: {updated_count}")
        
    except Exception as e:
        print(f"Error updating documents: {e}")

if __name__ == "__main__":
    asyncio.run(update_user_id())