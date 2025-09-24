#!/usr/bin/env python3
"""
Update existing attendance data to include new farms
"""

import asyncio
import random
from datetime import datetime, timedelta
from app.services.firebase_service import FirebaseService

class AttendanceUpdater:
    def __init__(self):
        self.firebase = FirebaseService()
        self.farmers = []
        self.farms = []
        
    async def init_data(self):
        """Load current farmers and farms"""
        print("Loading farmers and farms...")
        
        # Get farmers
        farmers_ref = self.firebase.db.collection('farmers')
        for doc in farmers_ref.stream():
            farmer_data = doc.to_dict()
            farmer_data['id'] = doc.id
            self.farmers.append(farmer_data)
            
        # Get farms  
        farms_ref = self.firebase.db.collection('farms')
        for doc in farms_ref.stream():
            farm_data = doc.to_dict()
            farm_data['id'] = doc.id
            self.farms.append(farm_data)
            
        print(f"Found {len(self.farmers)} farmers across {len(self.farms)} farms")
    
    async def regenerate_all_attendance(self):
        """Regenerate attendance data with new farm distribution"""
        print("🔄 Regenerating ALL attendance data with new farm assignments...")
        
        attendance_ref = self.firebase.db.collection('attendance')
        
        # Delete all existing attendance records
        print("🗑️  Deleting existing attendance records...")
        batch_size = 500
        
        while True:
            # Get a batch of documents
            docs = list(attendance_ref.limit(batch_size).stream())
            if not docs:
                break
                
            # Delete batch
            batch = self.firebase.db.batch()
            for doc in docs:
                batch.delete(doc.reference)
            batch.commit()
            print(f"   Deleted {len(docs)} records...")
        
        print("✅ All existing attendance records deleted")
        
        # Generate new attendance data for all 233 days
        print("📊 Generating new attendance data...")
        start_date = datetime.strptime('2025-01-01', '%Y-%m-%d')
        end_date = datetime.strptime('2025-08-21', '%Y-%m-%d')
        
        current_date = start_date
        total_records = 0
        day_count = 0
        
        while current_date <= end_date:
            day_count += 1
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Create attendance for this date
            records = await self.create_attendance_for_date(date_str)
            
            # Batch write to Firebase
            batch = self.firebase.db.batch()
            batch_count = 0
            
            for record in records:
                doc_ref = attendance_ref.document()
                batch.set(doc_ref, record)
                batch_count += 1
                
                if batch_count >= 500:
                    batch.commit()
                    batch = self.firebase.db.batch()
                    batch_count = 0
            
            # Commit remaining records
            if batch_count > 0:
                batch.commit()
            
            total_records += len(records)
            
            if day_count % 20 == 0:
                print(f"   Processed {day_count}/233 days ({total_records} records so far)")
            
            current_date += timedelta(days=1)
        
        print(f"✅ Generated {total_records} new attendance records for {day_count} days")
        return total_records
    
    async def create_attendance_for_date(self, date_str: str):
        """Create realistic attendance data for a specific date with all farms"""
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Weekend vs weekday attendance rates
        is_weekend = target_date.weekday() >= 5
        
        if is_weekend:
            base_attendance_rate = random.uniform(0.15, 0.25)  # 15-25% on weekends
        else:
            base_attendance_rate = random.uniform(0.60, 0.85)  # 60-85% on weekdays
        
        attendance_records = []
        
        # Group farmers by farm
        farmers_by_farm = {}
        for farmer in self.farmers:
            farm_id = farmer.get('farm_id')
            if farm_id:
                if farm_id not in farmers_by_farm:
                    farmers_by_farm[farm_id] = []
                farmers_by_farm[farm_id].append(farmer)
        
        # Generate attendance for each farm
        for farm_id, farm_farmers in farmers_by_farm.items():
            if not farm_farmers:
                continue
                
            # Find farm data
            farm = next((f for f in self.farms if f['id'] == farm_id), None)
            if not farm:
                continue
            
            # Each farm has slightly different attendance patterns
            farm_modifier = random.uniform(0.8, 1.2)  # ±20% variation
            farm_attendance_rate = min(0.95, base_attendance_rate * farm_modifier)
            
            # Select farmers for this farm
            num_attendees = max(1, int(len(farm_farmers) * farm_attendance_rate))
            selected_farmers = random.sample(farm_farmers, num_attendees)
            
            for farmer in selected_farmers:
                # Generate attendance record
                record = await self.create_farmer_attendance_record(farmer, farm, target_date, date_str)
                attendance_records.append(record)
        
        return attendance_records
    
    async def create_farmer_attendance_record(self, farmer, farm, target_date, date_str):
        """Create individual farmer attendance record"""
        # Random check-in time (5:30 AM - 9:00 AM)
        check_in_hour = random.randint(5, 8)
        check_in_minute = random.randint(0, 59)
        if check_in_hour == 5:
            check_in_minute = max(30, check_in_minute)
        
        check_in_time = target_date.replace(
            hour=check_in_hour, 
            minute=check_in_minute, 
            second=random.randint(0, 59),
            microsecond=0
        )
        
        # Check out probability (85%)
        check_out_time = None
        status = 'working'
        work_hours = None
        
        if random.random() < 0.85:
            work_duration = random.uniform(6, 10)
            check_out_time = check_in_time + timedelta(hours=work_duration)
            status = 'completed'
            work_hours = round(work_duration, 2)
        
        # Weather by season
        month = target_date.month
        if month in [12, 1, 2]:  # Winter
            weather = random.choices(
                ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                weights=[20, 30, 25, 15, 10]
            )[0]
        elif month in [3, 4, 5]:  # Spring
            weather = random.choices(
                ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                weights=[35, 25, 25, 10, 5]
            )[0]
        elif month in [6, 7, 8]:  # Summer
            weather = random.choices(
                ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                weights=[45, 20, 20, 10, 5]
            )[0]
        else:  # Fall
            weather = random.choices(
                ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                weights=[30, 25, 20, 15, 10]
            )[0]
        
        # Work types by season
        if month in [12, 1, 2, 3]:
            work_type = random.choices(
                ['pruning', 'maintenance', 'fertilizing', 'weeding', 'harvesting', 'planting'],
                weights=[30, 25, 20, 15, 5, 5]
            )[0]
        elif month in [4, 5, 6]:
            work_type = random.choices(
                ['planting', 'fertilizing', 'weeding', 'maintenance', 'pruning', 'harvesting'],
                weights=[25, 25, 25, 15, 5, 5]
            )[0]
        elif month in [7, 8, 9]:
            work_type = random.choices(
                ['harvesting', 'weeding', 'maintenance', 'fertilizing', 'pruning', 'planting'],
                weights=[40, 25, 15, 10, 5, 5]
            )[0]
        else:
            work_type = random.choices(
                ['maintenance', 'pruning', 'fertilizing', 'weeding', 'harvesting', 'planting'],
                weights=[30, 25, 20, 15, 7, 3]
            )[0]
        
        return {
            'farmer_id': farmer['id'],
            'farmer_name': farmer.get('name', farmer.get('full_name', 'Unknown')),
            'farm_id': farm['id'],
            'farm_name': farm.get('name', 'Unknown Farm'),
            'field_id': farmer.get('field_id'),
            'field_name': farmer.get('field_name'),
            'date': date_str,
            'check_in_time': check_in_time.isoformat(),
            'check_out_time': check_out_time.isoformat() if check_out_time else None,
            'face_confidence': round(random.uniform(0.82, 0.99), 3),
            'status': status,
            'work_hours': work_hours,
            'weather': weather,
            'work_type': work_type,
            'created_at': datetime.now().isoformat(),
        }

async def main():
    print("🚀 Updating attendance data with new farms...")
    print("📊 Database: kmou-aicofee (Primary)")
    
    updater = AttendanceUpdater()
    await updater.init_data()
    
    print(f"\\n⚠️  This will DELETE all existing attendance and regenerate with {len(updater.farms)} farms")
    print(f"📅 Will generate ~233 days of data for {len(updater.farmers)} farmers")
    print(f"📊 Estimated new records: ~{233 * len(updater.farmers) * 0.7:.0f}")
    
    # Regenerate all attendance data
    total_records = await updater.regenerate_all_attendance()
    
    print(f"\\n🎉 COMPLETION SUMMARY:")
    print(f"✅ Regenerated attendance data with {len(updater.farms)} farms")
    print(f"✅ Created {total_records} new attendance records")
    print(f"✅ All farms now have proportional attendance data")

if __name__ == "__main__":
    asyncio.run(main())