#!/usr/bin/env python3
"""
Script to create missing attendance data for Aug 23-31, 2025
"""
import asyncio
import random
from datetime import datetime, date, timedelta, timezone
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService

async def create_missing_attendance_data():
    """Create missing attendance data for Aug 23-31, 2025"""
    print("🚀 Creating missing attendance data for Aug 23-31, 2025...")
    
    firebase_service = FirebaseService()
    
    # Get all farmers
    farmers = await firebase_service.query_documents(
        "farmers",
        filters=[("is_active", "==", True)]
    )
    
    print(f"Found {len(farmers)} active farmers")
    
    if not farmers:
        print("❌ No farmers found!")
        return
    
    total_generated = 0
    
    # Generate data for Aug 23-31, 2025
    start_date = date(2025, 8, 23)
    end_date = date(2025, 8, 31)
    
    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        # Skip weekends
        if single_date.weekday() >= 5:  # Saturday=5, Sunday=6
            print(f"⏭️  Skipping {single_date.isoformat()} (weekend)")
            continue
        
        date_str = single_date.isoformat()
        print(f"📅 Creating attendance for {date_str}...")
        
        # 70-85% of farmers attend on any given day
        attendance_rate = random.uniform(0.7, 0.85)
        selected_farmers = random.sample(farmers, int(len(farmers) * attendance_rate))
        
        daily_count = 0
        for farmer in selected_farmers:
            farmer_id = farmer["id"]
            
            # Check if attendance already exists (avoid duplicates)
            existing_filters = [
                ("farmer_id", "==", farmer_id),
                ("date", "==", date_str)
            ]
            existing_records = await firebase_service.query_documents("attendance", filters=existing_filters)
            
            if existing_records:
                continue  # Skip if already exists
            
            # Generate realistic times
            check_in_hour = random.randint(6, 8)
            check_in_minute = random.randint(0, 59)
            work_hours = random.uniform(6, 10)
            work_minutes = int(work_hours * 60)
            
            check_in_time = datetime.combine(
                single_date, 
                datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute)
            ).replace(tzinfo=timezone(timedelta(hours=7)))  # Vietnam timezone
            
            check_out_time = check_in_time + timedelta(minutes=work_minutes)
            confidence = random.uniform(0.75, 0.95)
            status = "completed" if random.random() > 0.1 else "working"
            
            # Create attendance record
            timestamp = single_date.strftime("%Y%m%d") + "_" + str(random.randint(1000, 9999))
            doc_id = f"attendance_{farmer_id}_{timestamp}"
            
            attendance_data = {
                "id": doc_id,
                "farmer_id": farmer_id,
                "farm_id": farmer.get("farm_id", "default_farm"),
                "date": date_str,
                "check_in_time": check_in_time.isoformat(),
                "face_confidence": confidence,
                "status": status,
                "work_duration_minutes": work_minutes,
                "work_hours": work_hours,
                "created_by": "missing_data_generator",
                "check_in_location": {
                    "latitude": random.uniform(10.0, 10.1),
                    "longitude": random.uniform(105.8, 105.9)
                }
            }
            
            if status == "completed":
                attendance_data["check_out_time"] = check_out_time.isoformat()
                attendance_data["check_out_location"] = {
                    "latitude": random.uniform(10.0, 10.1),
                    "longitude": random.uniform(105.8, 105.9)
                }
            
            try:
                # Save to Firebase
                await firebase_service.save_document("attendance", doc_id, attendance_data)
                daily_count += 1
                farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown"
                print(f"  ✅ Created attendance for {farmer_name} (status: {status})")
            except Exception as e:
                farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown"
                print(f"  ❌ Error creating attendance for {farmer_name}: {e}")
        
        total_generated += daily_count
        print(f"  📊 Created {daily_count} records for {date_str}")
    
    print(f"\n🎉 Successfully created {total_generated} missing attendance records!")
    print(f"📅 Coverage: Aug 23-31, 2025 (weekdays only)")

if __name__ == "__main__":
    asyncio.run(create_missing_attendance_data())