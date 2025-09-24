#!/usr/bin/env python3
"""
Script to update face enrolled status for 75% of farmers
"""
import asyncio
import random
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService

async def update_face_enrolled():
    """Update face enrolled status for 75% of farmers"""
    print("🚀 Updating face enrolled status for 75% of farmers...")
    
    firebase_service = FirebaseService()
    
    # Get all farmers
    farmers = await firebase_service.query_documents("farmers")
    print(f"Found {len(farmers)} farmers")
    
    if not farmers:
        print("❌ No farmers found!")
        return
    
    # Select 75% of farmers for face enrollment
    enrollment_rate = 0.75
    selected_count = int(len(farmers) * enrollment_rate)
    selected_farmers = random.sample(farmers, selected_count)
    
    print(f"Updating face enrollment for {selected_count} farmers ({enrollment_rate*100}%)...")
    
    updated_count = 0
    
    for farmer in selected_farmers:
        farmer_id = farmer["id"]
        farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown"
        
        try:
            # Update farmer with face enrolled status
            update_data = {
                "face_enrolled": True,
                "has_face_enrolled": True,
                "face_enrollment_date": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await firebase_service.update_document("farmers", farmer_id, update_data)
            updated_count += 1
            print(f"  ✅ Updated face enrollment for {farmer_name}")
            
        except Exception as e:
            print(f"  ❌ Error updating {farmer_name}: {e}")
    
    print(f"\n🎉 Successfully updated face enrollment for {updated_count} farmers!")
    print(f"📊 Enrollment rate: {updated_count}/{len(farmers)} = {updated_count/len(farmers)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(update_face_enrolled())