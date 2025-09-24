#!/usr/bin/env python3
"""
Script to create dummy attendance data for today (2025-08-22)
"""

import asyncio
import random
from datetime import datetime, timezone, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService

class TodayAttendanceGenerator:
    def __init__(self):
        self.firebase = FirebaseService()
        self.farmers = []
        self.farms = []
        
        # Farm locations
        self.farm_locations = {
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
        
        # Work patterns
        self.work_patterns = {
            "early": {"check_in": (6, 0, 7, 0), "check_out": (14, 0, 15, 0)},
            "normal": {"check_in": (7, 0, 8, 0), "check_out": (16, 0, 17, 0)},
            "late": {"check_in": (8, 0, 9, 0), "check_out": (17, 0, 18, 0)},
        }
        
    def random_time_in_range(self, start_hour, start_min, end_hour, end_min):
        """Generate random time within given range"""
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        random_minutes = random.randint(start_minutes, end_minutes)
        
        hours = random_minutes // 60
        minutes = random_minutes % 60
        return hours, minutes

    def add_random_variation(self, lat, lng, meters=50):
        """Add random variation to coordinates (within meters)"""
        variation = meters / 111000
        new_lat = lat + random.uniform(-variation, variation)
        new_lng = lng + random.uniform(-variation, variation)
        return round(new_lat, 6), round(new_lng, 6)
        
    async def load_data(self):
        """Load farmers and farms data"""
        print("Loading farmers and farms...")
        
        # Load farmers
        farmers_docs = await self.firebase.query_documents("farmers")
        for farmer in farmers_docs:
            self.farmers.append(farmer)
            
        # Load farms  
        farms_docs = await self.firebase.query_documents("farms")
        for farm in farms_docs:
            self.farms.append(farm)
            
        print(f"Loaded {len(self.farmers)} farmers and {len(self.farms)} farms")
        
    async def create_attendance_record(self, farmer, farm, date, pattern="normal"):
        """Create a single attendance record for today"""
        farm_location = self.farm_locations.get(farm.get("id"), self.farm_locations["farm_son_pacamara"])
        work_pattern = self.work_patterns[pattern]
        
        # Generate check-in time
        check_in_hour, check_in_min = self.random_time_in_range(*work_pattern["check_in"])
        check_in_time = datetime.combine(
            date,
            datetime.min.time()
        ).replace(
            hour=check_in_hour,
            minute=check_in_min,
            second=random.randint(0, 59),
            tzinfo=timezone(timedelta(hours=7))  # Vietnam timezone
        )
        
        # Generate check-in location with variation
        check_in_lat, check_in_lng = self.add_random_variation(farm_location["lat"], farm_location["lng"])
        
        # Determine status based on current time
        current_hour = datetime.now().hour
        check_out_start_hour = work_pattern["check_out"][0]
        
        if current_hour >= check_out_start_hour + 1:
            status = "completed"
        elif current_hour >= check_out_start_hour:
            status = random.choice(["working", "completed"])
        else:
            status = "working"
        
        # Create attendance data
        attendance_data = {
            "farmer_id": farmer.get("id"),
            "farmer_name": farmer.get("full_name") or farmer.get("name") or "Unknown Farmer",
            "farm_id": farm.get("id"),
            "farm_name": farm.get("name") or farm_location["name"],
            "date": target_date.isoformat(),
            "check_in_time": check_in_time.isoformat(),
            "check_in_location": {
                "latitude": check_in_lat,
                "longitude": check_in_lng
            },
            "check_in_face_score": round(random.uniform(0.85, 0.98), 2),
            "status": status,
            "work_type": random.choice(['harvesting', 'planting', 'maintenance', 'inspection', 'irrigation']),
            "weather": random.choice(['sunny', 'cloudy', 'partly_cloudy']),
            "notes": random.choice([
                'Regular attendance',
                'Early arrival', 
                'On-time check-in',
                'Productive day',
                'Coffee harvesting',
                'Farm maintenance work',
                ''
            ]),
            "created_at": check_in_time.isoformat(),
            "updated_at": check_in_time.isoformat()
        }
        
        # If completed, add check-out data
        if status == "completed":
            check_out_hour, check_out_min = self.random_time_in_range(*work_pattern["check_out"])
            check_out_time = datetime.combine(
                target_date,
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
            check_out_lat, check_out_lng = self.add_random_variation(farm_location["lat"], farm_location["lng"])
            
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
        doc_id = f"attendance_{farmer.get('id')}_{timestamp}"
        attendance_data["id"] = doc_id
        
        return doc_id, attendance_data

    async def create_today_attendance(self):
        """Create dummy attendance data for today"""
        target_date = datetime(2025, 8, 22).date()  # August 22, 2025
        print(f"Creating dummy attendance data for: {target_date}")
        
        if not self.farmers:
            print("No farmers found!")
            return
            
        # Select random farmers for today's attendance (70-85% attendance rate)
        attendance_rate = random.uniform(0.7, 0.85)
        selected_farmers = random.sample(
            self.farmers, 
            int(len(self.farmers) * attendance_rate)
        )
        
        print(f"Creating attendance for {len(selected_farmers)} farmers...")
        
        created_count = 0
        
        for farmer in selected_farmers:
            # Assign random farm if farmer doesn't have one
            if self.farms:
                farm = random.choice(self.farms)
            else:
                # Create a default farm entry
                farm = {
                    "id": "farm_son_pacamara",
                    "name": "Sơn Pacamara Specialty Coffee Farm"
                }
            
            # Randomly assign work pattern
            pattern = random.choice(["early", "normal", "normal", "late"])  # More normal shifts
            
            try:
                doc_id, attendance_data = await self.create_attendance_record(
                    farmer=farmer,
                    farm=farm,
                    date=today,
                    pattern=pattern
                )
                
                # Save to Firebase
                await self.firebase.save_document("attendance", doc_id, attendance_data)
                
                created_count += 1
                farmer_name = farmer.get("full_name") or farmer.get("name") or "Unknown"
                print(f"  ✅ Created attendance for {farmer_name} (status: {attendance_data['status']})")
                
            except Exception as e:
                farmer_name = farmer.get("full_name") or farmer.get("name") or "Unknown"
                print(f"  ❌ Error creating attendance for {farmer_name}: {e}")
        
        print(f"\n🎉 Successfully created {created_count} attendance records for today!")
        
        # Show summary
        await self.show_today_summary(target_date)
        
    async def show_today_summary(self, date):
        """Show summary of today's attendance"""
        print(f"\n=== TODAY'S ATTENDANCE SUMMARY ({date}) ===")
        
        # Query today's attendance
        today_records = await self.firebase.query_documents(
            "attendance",
            filters=[("date", "==", date.isoformat())]
        )
        
        working_count = len([r for r in today_records if r.get("status") == "working"])
        completed_count = len([r for r in today_records if r.get("status") == "completed"])
        
        print(f"Total attendance: {len(today_records)} farmers")
        print(f"  - Working: {working_count}")
        print(f"  - Completed: {completed_count}")
        
        # Group by farm
        farms_summary = {}
        for record in today_records:
            farm_name = record.get("farm_name", "Unknown Farm")
            if farm_name not in farms_summary:
                farms_summary[farm_name] = {"working": 0, "completed": 0}
            farms_summary[farm_name][record.get("status", "working")] += 1
        
        print(f"\nBy farm:")
        for farm_name, counts in farms_summary.items():
            total = counts["working"] + counts["completed"]
            print(f"  {farm_name}: {total} ({counts['working']} working, {counts['completed']} completed)")

async def main():
    generator = TodayAttendanceGenerator()
    
    print("🚀 Creating dummy attendance data for today...")
    
    # Load data
    await generator.load_data()
    
    # Create today's attendance
    await generator.create_today_attendance()
    
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())