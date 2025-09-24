#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime, timedelta, timezone
import random
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
from app.core.config import settings

# Initialize services
firebase_service = FirebaseService()

# Define work time patterns
WORK_PATTERNS = {
    "early": {"check_in": (6, 0, 7, 0), "check_out": (14, 0, 15, 0)},  # 6:00-7:00 AM check-in, 2:00-3:00 PM check-out
    "normal": {"check_in": (7, 0, 8, 0), "check_out": (16, 0, 17, 0)},  # 7:00-8:00 AM check-in, 4:00-5:00 PM check-out
    "late": {"check_in": (8, 0, 9, 0), "check_out": (17, 0, 18, 0)},  # 8:00-9:00 AM check-in, 5:00-6:00 PM check-out
}

# Location data for different farms
FARM_LOCATIONS = {
    "farm_son_pacamara": {
        "lat": 11.9404,
        "lng": 108.4583,
        "name": "Sơn Pacamara Specialty Coffee Farm"
    },
    "farm_ta_nung": {
        "lat": 11.8935,
        "lng": 108.4170,
        "name": "Em Tà Nung Coffee Farm"
    },
    "farm_future_coffee": {
        "lat": 11.9123,
        "lng": 108.4456,
        "name": "Future Coffee Farm Vietnam"
    }
}

def random_time_in_range(start_hour, start_min, end_hour, end_min):
    """Generate random time within given range"""
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min
    random_minutes = random.randint(start_minutes, end_minutes)
    
    hours = random_minutes // 60
    minutes = random_minutes % 60
    return hours, minutes

def add_random_variation(lat, lng, meters=50):
    """Add random variation to coordinates (within meters)"""
    # Approximately 1 degree = 111km
    variation = meters / 111000
    new_lat = lat + random.uniform(-variation, variation)
    new_lng = lng + random.uniform(-variation, variation)
    return round(new_lat, 6), round(new_lng, 6)

async def create_attendance_record(farmer_id, farmer_name, farm_id, date, pattern="normal", status="completed"):
    """Create a single attendance record"""
    farm_location = FARM_LOCATIONS.get(farm_id, FARM_LOCATIONS["farm_son_pacamara"])
    work_pattern = WORK_PATTERNS[pattern]
    
    # Generate check-in time
    check_in_hour, check_in_min = random_time_in_range(*work_pattern["check_in"])
    check_in_time = datetime.combine(
        date,
        datetime.min.time()
    ).replace(
        hour=check_in_hour,
        minute=check_in_min,
        second=random.randint(0, 59),
        tzinfo=timezone(timedelta(hours=7))  # Vietnam timezone
    )
    
    # Generate check-in location with small variation
    check_in_lat, check_in_lng = add_random_variation(farm_location["lat"], farm_location["lng"])
    
    # Create attendance data
    attendance_data = {
        "farmer_id": farmer_id,
        "farmer_name": farmer_name,
        "farm_id": farm_id,
        "farm_name": farm_location["name"],
        "date": date.isoformat(),
        "check_in_time": check_in_time.isoformat(),
        "check_in_location": {
            "latitude": check_in_lat,
            "longitude": check_in_lng
        },
        "check_in_face_score": round(random.uniform(0.85, 0.98), 2),
        "status": status,
        "created_at": check_in_time.isoformat(),
        "updated_at": check_in_time.isoformat()
    }
    
    # If completed, add check-out data
    if status == "completed":
        check_out_hour, check_out_min = random_time_in_range(*work_pattern["check_out"])
        check_out_time = datetime.combine(
            date,
            datetime.min.time()
        ).replace(
            hour=check_out_hour,
            minute=check_out_min,
            second=random.randint(0, 59),
            tzinfo=timezone(timedelta(hours=7))
        )
        
        # Calculate work duration
        work_duration = check_out_time - check_in_time
        work_duration_minutes = int(work_duration.total_seconds() / 60)
        work_hours = work_duration_minutes / 60
        
        # Generate check-out location
        check_out_lat, check_out_lng = add_random_variation(farm_location["lat"], farm_location["lng"])
        
        attendance_data.update({
            "check_out_time": check_out_time.isoformat(),
            "check_out_location": {
                "latitude": check_out_lat,
                "longitude": check_out_lng
            },
            "check_out_face_score": round(random.uniform(0.85, 0.98), 2),
            "work_duration_minutes": work_duration_minutes,
            "work_hours": round(work_hours, 2),
            "updated_at": check_out_time.isoformat()
        })
    
    # Generate document ID
    timestamp = check_in_time.strftime("%Y%m%d_%H%M%S")
    doc_id = f"attendance_{farmer_id}_{timestamp}"
    attendance_data["id"] = doc_id
    
    # Save to Firebase
    await firebase_service.save_document("attendance", doc_id, attendance_data)
    
    return attendance_data

async def main():
    """Create dummy attendance data"""
    print("Creating dummy attendance data...")
    
    # Get all farmers
    farmers = await firebase_service.query_documents("farmers")
    print(f"Found {len(farmers)} farmers")
    
    # Filter farmers by farm
    farmers_by_farm = {}
    for farmer in farmers:
        farm_id = farmer.get("farm_id", "default_farm")
        if farm_id not in farmers_by_farm:
            farmers_by_farm[farm_id] = []
        farmers_by_farm[farm_id].append(farmer)
    
    # Dates - Fix to use correct dates
    yesterday = datetime(2025, 6, 12).date()  # June 12, 2025
    today = datetime(2025, 6, 13).date()      # June 13, 2025
    
    created_count = 0
    
    # Create attendance for yesterday (all completed)
    print(f"\nCreating attendance for yesterday ({yesterday})...")
    for farm_id, farm_farmers in farmers_by_farm.items():
        if farm_id not in FARM_LOCATIONS:
            continue
            
        # Randomly select 70-90% of farmers for attendance
        attendance_rate = random.uniform(0.7, 0.9)
        selected_farmers = random.sample(
            farm_farmers, 
            int(len(farm_farmers) * attendance_rate)
        )
        
        for farmer in selected_farmers:
            farmer_id = farmer.get("id")
            farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown"
            
            # Randomly assign work pattern
            pattern = random.choice(["early", "normal", "normal", "late"])  # More normal shifts
            
            try:
                attendance = await create_attendance_record(
                    farmer_id=farmer_id,
                    farmer_name=farmer_name,
                    farm_id=farm_id,
                    date=yesterday,
                    pattern=pattern,
                    status="completed"
                )
                created_count += 1
                print(f"  Created attendance for {farmer_name} at {farm_id}")
            except Exception as e:
                print(f"  Error creating attendance for {farmer_name}: {e}")
    
    # Create attendance for today (mix of working and completed)
    print(f"\nCreating attendance for today ({today})...")
    current_hour = datetime.now().hour
    
    for farm_id, farm_farmers in farmers_by_farm.items():
        if farm_id not in FARM_LOCATIONS:
            continue
            
        # Randomly select 60-80% of farmers for today's attendance
        attendance_rate = random.uniform(0.6, 0.8)
        selected_farmers = random.sample(
            farm_farmers, 
            int(len(farm_farmers) * attendance_rate)
        )
        
        for farmer in selected_farmers:
            farmer_id = farmer.get("id")
            farmer_name = farmer.get("name") or farmer.get("full_name") or "Unknown"
            
            # Randomly assign work pattern
            pattern = random.choice(["early", "normal", "normal", "late"])
            
            # Determine status based on current time and pattern
            work_pattern = WORK_PATTERNS[pattern]
            check_out_start_hour = work_pattern["check_out"][0]
            
            # If current time is past typical check-out time, mark as completed
            if current_hour >= check_out_start_hour + 1:
                status = "completed"
            elif current_hour >= check_out_start_hour:
                # Some might have checked out
                status = random.choice(["working", "completed"])
            else:
                status = "working"
            
            try:
                attendance = await create_attendance_record(
                    farmer_id=farmer_id,
                    farmer_name=farmer_name,
                    farm_id=farm_id,
                    date=today,
                    pattern=pattern,
                    status=status
                )
                created_count += 1
                print(f"  Created attendance for {farmer_name} at {farm_id} (status: {status})")
            except Exception as e:
                print(f"  Error creating attendance for {farmer_name}: {e}")
    
    print(f"\nTotal attendance records created: {created_count}")
    
    # Print summary
    print("\nSummary by farm:")
    for farm_id, location in FARM_LOCATIONS.items():
        # Count yesterday's attendance
        yesterday_records = await firebase_service.query_documents(
            "attendance",
            filters=[
                ("farm_id", "==", farm_id),
                ("date", "==", yesterday.isoformat())
            ]
        )
        
        # Count today's attendance
        today_records = await firebase_service.query_documents(
            "attendance",
            filters=[
                ("farm_id", "==", farm_id),
                ("date", "==", today.isoformat())
            ]
        )
        
        today_working = [r for r in today_records if r.get("status") == "working"]
        today_completed = [r for r in today_records if r.get("status") == "completed"]
        
        print(f"\n{location['name']}:")
        print(f"  Yesterday: {len(yesterday_records)} farmers")
        print(f"  Today: {len(today_records)} farmers total")
        print(f"    - Working: {len(today_working)}")
        print(f"    - Completed: {len(today_completed)}")

if __name__ == "__main__":
    asyncio.run(main())