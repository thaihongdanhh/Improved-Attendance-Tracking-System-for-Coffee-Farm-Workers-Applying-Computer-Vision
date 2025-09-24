#!/usr/bin/env python3
"""
Script to fill missing attendance dates with dummy data
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict
from app.services.firebase_service import FirebaseService

class MissingAttendanceFiller:
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
        
    async def get_missing_dates(self):
        """Find missing dates in attendance data"""
        print("Analyzing attendance data gaps...")
        
        attendance_ref = self.firebase.db.collection('attendance')
        all_docs = list(attendance_ref.stream())
        
        # Get all existing dates
        existing_dates = set()
        for doc in all_docs:
            data = doc.to_dict()
            if 'date' in data:
                existing_dates.add(data['date'])
        
        # Find missing dates in range
        start_date = datetime.strptime('2025-01-01', '%Y-%m-%d')
        end_date = datetime.strptime('2025-08-21', '%Y-%m-%d')
        
        missing_dates = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in existing_dates:
                missing_dates.append(date_str)
            current_date += timedelta(days=1)
        
        print(f"Found {len(missing_dates)} missing dates")
        return sorted(missing_dates)
    
    async def create_attendance_for_date(self, date_str: str):
        """Create realistic attendance data for a specific date"""
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Weekend có ít attendance hơn (20-30% farmers)
        is_weekend = target_date.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        if is_weekend:
            attendance_rate = random.uniform(0.2, 0.35)  # 20-35% on weekends
        else:
            attendance_rate = random.uniform(0.65, 0.95)  # 65-95% on weekdays
        
        # Select random farmers for this day
        num_farmers = max(1, int(len(self.farmers) * attendance_rate))
        selected_farmers = random.sample(self.farmers, num_farmers)
        
        attendance_records = []
        
        for farmer in selected_farmers:
            # Usually work at assigned farm, sometimes at others (90% vs 10%)
            if farmer.get('farm_id') and random.random() < 0.9:
                assigned_farm = next((f for f in self.farms if f['id'] == farmer['farm_id']), None)
                farm = assigned_farm if assigned_farm else random.choice(self.farms)
            else:
                farm = random.choice(self.farms)
            
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
            
            # Most people check out (85% rate)
            check_out_time = None
            status = 'working'
            work_hours = None
            
            if random.random() < 0.85:  # 85% check out
                # Work 6-10 hours
                work_duration = random.uniform(6, 10)
                check_out_time = check_in_time + timedelta(hours=work_duration)
                status = 'completed'
                work_hours = round(work_duration, 2)
            
            # Weather patterns (more realistic by season)
            month = target_date.month
            if month in [12, 1, 2]:  # Winter - more cloudy/rainy
                weather = random.choices(
                    ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                    weights=[20, 30, 25, 15, 10]
                )[0]
            elif month in [3, 4, 5]:  # Spring - mixed
                weather = random.choices(
                    ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                    weights=[35, 25, 25, 10, 5]
                )[0]
            elif month in [6, 7, 8]:  # Summer - more sunny but some rain
                weather = random.choices(
                    ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                    weights=[45, 20, 20, 10, 5]
                )[0]
            else:  # Fall - mixed with more overcast
                weather = random.choices(
                    ['sunny', 'cloudy', 'partly_cloudy', 'light_rain', 'overcast'],
                    weights=[30, 25, 20, 15, 10]
                )[0]
            
            # Work types based on season
            if month in [12, 1, 2, 3]:  # Winter/early spring - maintenance, pruning
                work_type = random.choices(
                    ['pruning', 'maintenance', 'fertilizing', 'weeding', 'harvesting', 'planting'],
                    weights=[30, 25, 20, 15, 5, 5]
                )[0]
            elif month in [4, 5, 6]:  # Late spring/early summer - planting, fertilizing
                work_type = random.choices(
                    ['planting', 'fertilizing', 'weeding', 'maintenance', 'pruning', 'harvesting'],
                    weights=[25, 25, 25, 15, 5, 5]
                )[0]
            elif month in [7, 8, 9]:  # Summer/early fall - harvesting peak
                work_type = random.choices(
                    ['harvesting', 'weeding', 'maintenance', 'fertilizing', 'pruning', 'planting'],
                    weights=[40, 25, 15, 10, 5, 5]
                )[0]
            else:  # Late fall - post-harvest maintenance
                work_type = random.choices(
                    ['maintenance', 'pruning', 'fertilizing', 'weeding', 'harvesting', 'planting'],
                    weights=[30, 25, 20, 15, 7, 3]
                )[0]
            
            attendance_data = {
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
            
            attendance_records.append(attendance_data)
        
        return attendance_records
    
    async def fill_missing_dates(self, missing_dates: List[str]):
        """Fill all missing dates with attendance data"""
        print(f"Filling {len(missing_dates)} missing dates...")
        
        attendance_ref = self.firebase.db.collection('attendance')
        total_records = 0
        
        for i, date_str in enumerate(missing_dates):
            print(f"Processing {date_str} ({i+1}/{len(missing_dates)})...")
            
            # Create attendance records for this date
            records = await self.create_attendance_for_date(date_str)
            
            # Batch write to Firebase (500 records at a time)
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
            print(f"  ✅ Added {len(records)} records for {date_str}")
        
        print(f"✅ Successfully filled {len(missing_dates)} missing dates with {total_records} total records!")
        return total_records

async def main():
    print("🚀 Starting missing attendance dates filling...")
    print("📊 Current Database: kmou-aicofee (Primary)")
    
    filler = MissingAttendanceFiller()
    
    # Initialize data
    await filler.init_data()
    
    # Find missing dates
    missing_dates = await filler.get_missing_dates()
    
    if not missing_dates:
        print("✅ No missing dates found - database is complete!")
        return
    
    print(f"\n📋 Missing dates to fill: {len(missing_dates)}")
    print(f"📅 First missing: {missing_dates[0]}")
    print(f"📅 Last missing: {missing_dates[-1]}")
    
    # Confirm before proceeding
    print(f"\n⚠️  This will add approximately {len(missing_dates) * 30} attendance records")
    print("🚀 Auto-proceeding to fill missing dates...")
    
    # Fill missing dates
    total_added = await filler.fill_missing_dates(missing_dates)
    
    # Final summary
    print(f"\n🎉 COMPLETION SUMMARY:")
    print(f"✅ Filled {len(missing_dates)} missing dates")
    print(f"✅ Added {total_added} new attendance records")
    print(f"✅ Database: kmou-aicofee is now complete!")

if __name__ == "__main__":
    asyncio.run(main())