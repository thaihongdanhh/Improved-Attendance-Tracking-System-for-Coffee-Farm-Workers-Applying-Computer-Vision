#!/usr/bin/env python3
"""
Script to create dummy attendance data for Firebase
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict
from app.services.firebase_service import FirebaseService

class AttendanceDummyDataGenerator:
    def __init__(self):
        self.firebase = FirebaseService()
        self.farmers = []
        self.farms = []
        
    async def init_data(self):
        """Load farmers and farms data"""
        print("Loading existing farmers and farms...")
        
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
            
        print(f"Found {len(self.farmers)} farmers and {len(self.farms)} farms")
        
    async def fix_existing_attendance(self):
        """Fix existing attendance records that are missing farmer names"""
        print("Fixing existing attendance records...")
        
        attendance_ref = self.firebase.db.collection('attendance')
        batch = self.firebase.db.batch()
        
        count = 0
        for doc in attendance_ref.stream():
            attendance_data = doc.to_dict()
            
            # Skip if farmer_name already exists
            if attendance_data.get('farmer_name'):
                continue
                
            # Find farmer by farmer_id
            farmer_id = attendance_data.get('farmer_id')
            if farmer_id:
                farmer = next((f for f in self.farmers if f['id'] == farmer_id), None)
                if farmer:
                    # Update with farmer name
                    batch.update(doc.reference, {
                        'farmer_name': farmer.get('full_name', farmer.get('name', 'Unknown Farmer'))
                    })
                    count += 1
            else:
                # Assign random farmer if no farmer_id
                random_farmer = random.choice(self.farmers)
                batch.update(doc.reference, {
                    'farmer_id': random_farmer['id'],
                    'farmer_name': random_farmer.get('full_name', random_farmer.get('name', 'Unknown Farmer'))
                })
                count += 1
                
            # Commit batch every 500 operations
            if count % 500 == 0:
                await asyncio.to_thread(batch.commit)
                batch = self.firebase.db.batch()
                print(f"Updated {count} records...")
                
        # Commit remaining
        if count % 500 != 0:
            await asyncio.to_thread(batch.commit)
            
        print(f"Fixed {count} existing attendance records")
        
    async def create_dummy_attendance(self, days_back: int = 90, records_per_day: int = 15):
        """Create dummy attendance records"""
        print(f"Creating dummy attendance for {days_back} days with ~{records_per_day} records per day...")
        
        if not self.farmers or not self.farms:
            print("No farmers or farms found!")
            return
            
        start_date = datetime.now() - timedelta(days=days_back)
        attendance_records = []
        
        for day in range(days_back):
            current_date = start_date + timedelta(days=day)
            
            # Skip weekends sometimes
            if current_date.weekday() >= 5 and random.random() < 0.3:
                continue
                
            # Random number of attendance records per day
            daily_records = random.randint(records_per_day - 5, records_per_day + 10)
            
            # Select random farmers for the day
            daily_farmers = random.sample(self.farmers, min(daily_records, len(self.farmers)))
            
            for farmer in daily_farmers:
                # Random check-in time between 6:00 and 10:00 AM
                check_in_hour = random.randint(6, 9)
                check_in_minute = random.randint(0, 59)
                check_in_time = current_date.replace(hour=check_in_hour, minute=check_in_minute, second=0)
                
                # Random check-out time between 5:00 and 8:00 PM (or None for some records)
                check_out_time = None
                if random.random() > 0.1:  # 90% chance of check-out
                    check_out_hour = random.randint(17, 19)
                    check_out_minute = random.randint(0, 59)  
                    check_out_time = current_date.replace(hour=check_out_hour, minute=check_out_minute, second=0)
                
                # Random farm
                farm = random.choice(self.farms)
                
                # Generate attendance record
                attendance_record = {
                    'id': f"attendance_{current_date.strftime('%Y%m%d')}_{farmer['id']}_{random.randint(1000, 9999)}",
                    'farmer_id': farmer['id'],
                    'farmer_name': farmer.get('full_name', farmer.get('name', 'Unknown Farmer')),
                    'farm_id': farm['id'],
                    'farm_name': farm['name'],
                    'date': current_date.strftime('%Y-%m-%d'),
                    'check_in_time': check_in_time.strftime('%Y-%m-%dT%H:%M:%S+07:00'),
                    'check_out_time': check_out_time.strftime('%Y-%m-%dT%H:%M:%S+07:00') if check_out_time else None,
                    'status': 'present',
                    'notes': random.choice([
                        'Regular attendance',
                        'Early arrival', 
                        'On-time check-in',
                        'Productive day',
                        '',
                        'Coffee harvesting',
                        'Farm maintenance work'
                    ]),
                    'created_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00'),
                    'updated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00'),
                    'check_in_method': random.choice(['face_recognition', 'manual', 'qr_code']),
                    'location': f"{farm['location']}",
                    'weather': random.choice(['sunny', 'cloudy', 'partly_cloudy', 'rainy']),
                    'work_type': random.choice(['harvesting', 'planting', 'maintenance', 'inspection', 'irrigation'])
                }
                
                attendance_records.append(attendance_record)
        
        # Batch write to Firebase
        print(f"Writing {len(attendance_records)} attendance records to Firebase...")
        
        batch = self.firebase.db.batch()
        count = 0
        
        for record in attendance_records:
            doc_ref = self.firebase.db.collection('attendance').document()
            batch.set(doc_ref, record)
            count += 1
            
            # Commit batch every 500 operations
            if count % 500 == 0:
                await asyncio.to_thread(batch.commit)
                batch = self.firebase.db.batch()
                print(f"Written {count}/{len(attendance_records)} records...")
                
        # Commit remaining
        if count % 500 != 0:
            await asyncio.to_thread(batch.commit)
            
        print(f"✅ Successfully created {len(attendance_records)} dummy attendance records!")
        
    async def show_summary(self):
        """Show summary of attendance data"""
        print("\n=== ATTENDANCE SUMMARY ===")
        
        attendance_ref = self.firebase.db.collection('attendance')
        total_count = 0
        recent_records = []
        
        for doc in attendance_ref.limit(10).order_by('created_at', direction='DESCENDING').stream():
            total_count += 1
            data = doc.to_dict()
            data['id'] = doc.id
            recent_records.append(data)
            
        # Get total count
        all_docs = attendance_ref.stream()
        total_count = len(list(all_docs))
        
        print(f"Total attendance records: {total_count}")
        print("\nRecent records:")
        for record in recent_records[:5]:
            print(f"- {record.get('date')} | {record.get('farmer_name', 'N/A')} | {record.get('farm_name', 'N/A')}")

async def main():
    generator = AttendanceDummyDataGenerator()
    
    print("🚀 Starting attendance data generation...")
    
    # Initialize data
    await generator.init_data()
    
    # Fix existing records
    await generator.fix_existing_attendance()
    
    # Create new dummy records
    await generator.create_dummy_attendance(days_back=180, records_per_day=20)
    
    # Show summary
    await generator.show_summary()
    
    print("✅ Attendance data generation completed!")

if __name__ == "__main__":
    asyncio.run(main())