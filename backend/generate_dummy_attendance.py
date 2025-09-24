#!/usr/bin/env python3
"""
Script to generate dummy attendance data for missing days
"""
import asyncio
import random
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict
import json
import os
import sys

# Add the app directory to Python path
sys.path.append('/mnt/data/AIFace/AICoffeePortal/backend')

from app.services.firebase_service import FirebaseService

class AttendanceDummyGenerator:
    def __init__(self):
        self.firebase_service = FirebaseService()
        
    async def get_farmers(self) -> List[Dict]:
        """Get all active farmers from database"""
        try:
            farmers = await self.firebase_service.query_documents(
                "farmers",
                filters=[("is_active", "==", True)]
            )
            print(f"Found {len(farmers)} active farmers")
            return farmers
        except Exception as e:
            print(f"Error getting farmers: {e}")
            return []
    
    async def get_farms(self) -> List[Dict]:
        """Get all farms from database"""
        try:
            farms = await self.firebase_service.query_documents("farms")
            print(f"Found {len(farms)} farms")
            return farms
        except Exception as e:
            print(f"Error getting farms: {e}")
            return []
    
    async def check_existing_attendance(self, farmer_id: str, target_date: date) -> bool:
        """Check if attendance already exists for farmer on specific date"""
        try:
            date_str = target_date.isoformat()
            filters = [
                ("farmer_id", "==", farmer_id),
                ("date", "==", date_str)
            ]
            
            records = await self.firebase_service.query_documents("attendance", filters=filters)
            return len(records) > 0
        except Exception as e:
            print(f"Error checking existing attendance: {e}")
            return True  # Assume exists to avoid duplicates on error
    
    def generate_realistic_times(self, target_date: date) -> Dict:
        """Generate realistic check-in and check-out times"""
        # Check-in times: 6:00 - 9:00 AM
        check_in_hour = random.randint(6, 8)
        check_in_minute = random.randint(0, 59)
        
        # Work duration: 6-10 hours
        work_hours = random.uniform(6, 10)
        work_minutes = int(work_hours * 60)
        
        check_in_time = datetime.combine(
            target_date, 
            datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute)
        ).replace(tzinfo=timezone.utc)
        
        check_out_time = check_in_time + timedelta(minutes=work_minutes)
        
        # Face confidence: 75-95%
        confidence = random.uniform(0.75, 0.95)
        
        # 10% chance of no checkout (still working)
        status = "completed" if random.random() > 0.1 else "working"
        
        result = {
            "check_in_time": check_in_time.isoformat(),
            "work_duration_minutes": work_minutes,
            "work_hours": work_hours,
            "confidence": confidence,
            "status": status
        }
        
        if status == "completed":
            result["check_out_time"] = check_out_time.isoformat()
        
        return result
    
    async def generate_attendance_for_date(self, target_date: date, farmers: List[Dict]) -> int:
        """Generate attendance data for a specific date"""
        generated_count = 0
        
        # 70-90% of farmers attend on any given day
        attendance_rate = random.uniform(0.7, 0.9)
        attending_farmers = random.sample(farmers, int(len(farmers) * attendance_rate))
        
        print(f"Generating attendance for {target_date.isoformat()}: {len(attending_farmers)}/{len(farmers)} farmers")
        
        for farmer in attending_farmers:
            farmer_id = farmer["id"]
            
            # Check if attendance already exists
            if await self.check_existing_attendance(farmer_id, target_date):
                print(f"  Skipping {farmer_id} - attendance already exists")
                continue
            
            # Generate realistic times
            times_data = self.generate_realistic_times(target_date)
            
            # Create attendance record
            timestamp = target_date.strftime("%Y%m%d") + "_" + farmer_id[:8]
            doc_id = f"attendance_{farmer_id}_{timestamp}"
            
            attendance_data = {
                "id": doc_id,
                "farmer_id": farmer_id,
                "farm_id": farmer.get("farm_id", "default_farm"),
                "date": target_date.isoformat(),
                "check_in_time": times_data["check_in_time"],
                "face_confidence": times_data["confidence"],
                "status": times_data["status"],
                "work_duration_minutes": times_data["work_duration_minutes"],
                "work_hours": times_data["work_hours"],
                "created_by": "system_dummy_generator",
                "check_in_location": {
                    "latitude": random.uniform(10.0, 10.1),  # Vietnam coordinates
                    "longitude": random.uniform(105.8, 105.9)
                }
            }
            
            # Add check-out data if completed
            if times_data["status"] == "completed":
                attendance_data["check_out_time"] = times_data["check_out_time"]
                attendance_data["check_out_location"] = {
                    "latitude": random.uniform(10.0, 10.1),
                    "longitude": random.uniform(105.8, 105.9)
                }
            
            try:
                await self.firebase_service.save_document("attendance", doc_id, attendance_data)
                generated_count += 1
                print(f"  ✅ Generated attendance for {farmer.get('name', farmer_id)}")
            except Exception as e:
                print(f"  ❌ Error generating attendance for {farmer_id}: {e}")
        
        return generated_count
    
    async def generate_dummy_data(self, days_back: int = 30):
        """Generate dummy attendance data for the last N days"""
        print(f"🚀 Starting dummy attendance data generation for last {days_back} days")
        
        # Get farmers and farms
        farmers = await self.get_farmers()
        if not farmers:
            print("❌ No farmers found. Cannot generate attendance data.")
            return
        
        farms = await self.get_farms()
        print(f"📊 Working with {len(farmers)} farmers across {len(farms)} farms")
        
        total_generated = 0
        
        # Generate data for each day
        for i in range(days_back):
            target_date = date.today() - timedelta(days=i+1)  # Skip today
            
            # Skip weekends (optional - comment out if farms work on weekends)
            if target_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                print(f"⏭️  Skipping {target_date.isoformat()} (weekend)")
                continue
            
            daily_count = await self.generate_attendance_for_date(target_date, farmers)
            total_generated += daily_count
            
            # Small delay to avoid overwhelming Firebase
            await asyncio.sleep(0.1)
        
        print(f"🎉 Dummy data generation completed!")
        print(f"📈 Generated {total_generated} attendance records across {days_back} days")

async def main():
    """Main function to run the dummy data generator"""
    generator = AttendanceDummyGenerator()
    
    # Generate dummy data for last 30 days
    days_back = 30
    if len(sys.argv) > 1:
        try:
            days_back = int(sys.argv[1])
        except ValueError:
            print("Invalid number of days. Using default: 30")
    
    await generator.generate_dummy_data(days_back)

if __name__ == "__main__":
    asyncio.run(main())