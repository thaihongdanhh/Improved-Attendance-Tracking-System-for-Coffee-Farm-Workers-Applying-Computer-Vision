#!/usr/bin/env python3
"""
Script to add more realistic farms to the database
"""

import asyncio
from datetime import datetime
from app.services.firebase_service import FirebaseService

class FarmExpander:
    def __init__(self):
        self.firebase = FirebaseService()
        
    def get_additional_farms(self):
        """Create realistic coffee farm data for Vietnam"""
        additional_farms = [
            {
                "name": "Cầu Đất Coffee Estate",
                "location": "Cầu Đất, Đà Lạt, Lâm Đồng, Vietnam",
                "coordinates": {
                    "latitude": 11.9150,
                    "longitude": 108.4200
                },
                "area_hectares": 42.5,
                "elevation": 1350,
                "coffee_varieties": ["Arabica", "Catimor", "Bourbon"],
                "established_year": 1995,
                "owner": "Cầu Đất Coffee Corporation",
                "contact": "+84 263 123 456",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - High Plateau", "area": 12.5},
                    {"id": "field_b", "name": "Field B - Slope Terrace", "area": 15.0},
                    {"id": "field_c", "name": "Field C - Valley Bottom", "area": 8.0},
                    {"id": "field_d", "name": "Field D - West Ridge", "area": 7.0}
                ]
            },
            {
                "name": "Mê Linh Coffee Plantation",
                "location": "Mê Linh, Lâm Hà, Lâm Đồng, Vietnam",
                "coordinates": {
                    "latitude": 11.7500,
                    "longitude": 108.3167
                },
                "area_hectares": 28.0,
                "elevation": 1200,
                "coffee_varieties": ["Robusta", "Arabica"],
                "established_year": 2003,
                "owner": "Mê Linh Agricultural Cooperative",
                "contact": "+84 263 234 567",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - Main Block", "area": 15.0},
                    {"id": "field_b", "name": "Field B - South Wing", "area": 8.0},
                    {"id": "field_c", "name": "Field C - Nursery Area", "area": 5.0}
                ]
            },
            {
                "name": "Chu Yang Sin Highland Farm",
                "location": "Chu Yang Sin, Đắk Lắk, Vietnam", 
                "coordinates": {
                    "latitude": 12.3833,
                    "longitude": 108.6833
                },
                "area_hectares": 67.2,
                "elevation": 800,
                "coffee_varieties": ["Robusta", "Catimor", "TR4"],
                "established_year": 1988,
                "owner": "Highland Coffee Enterprises",
                "contact": "+84 262 345 678",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - North Valley", "area": 20.0},
                    {"id": "field_b", "name": "Field B - Central Plain", "area": 22.2},
                    {"id": "field_c", "name": "Field C - South Hills", "area": 15.0},
                    {"id": "field_d", "name": "Field D - Riverside Block", "area": 10.0}
                ]
            },
            {
                "name": "Buôn Ma Thuột Heritage Coffee",
                "location": "Buôn Ma Thuột, Đắk Lắk, Vietnam",
                "coordinates": {
                    "latitude": 12.6647,
                    "longitude": 108.0378
                },
                "area_hectares": 85.5,
                "elevation": 500,
                "coffee_varieties": ["Robusta", "Excelsa", "Liberica"],
                "established_year": 1975,
                "owner": "Buôn Ma Thuột Coffee Group",
                "contact": "+84 262 456 789",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - Heritage Block", "area": 25.0},
                    {"id": "field_b", "name": "Field B - Modern Wing", "area": 30.5},
                    {"id": "field_c", "name": "Field C - Experimental Plot", "area": 15.0},
                    {"id": "field_d", "name": "Field D - Processing Area", "area": 10.0},
                    {"id": "field_e", "name": "Field E - Storage Complex", "area": 5.0}
                ]
            },
            {
                "name": "Kon Tum Mountain Coffee",
                "location": "Kon Tum, Kon Tum Province, Vietnam",
                "coordinates": {
                    "latitude": 14.3497,
                    "longitude": 108.0004
                },
                "area_hectares": 31.8,
                "elevation": 650,
                "coffee_varieties": ["Arabica", "Catimor"],
                "established_year": 2008,
                "owner": "Kon Tum Mountain Farmers Union",
                "contact": "+84 260 567 890",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - Mountain Slope", "area": 18.0},
                    {"id": "field_b", "name": "Field B - Valley Floor", "area": 8.8},
                    {"id": "field_c", "name": "Field C - Shade Garden", "area": 5.0}
                ]
            },
            {
                "name": "Gia Lai Sustainable Coffee Farm",
                "location": "Pleiku, Gia Lai Province, Vietnam", 
                "coordinates": {
                    "latitude": 13.9833,
                    "longitude": 108.0000
                },
                "area_hectares": 55.7,
                "elevation": 780,
                "coffee_varieties": ["Robusta", "Arabica", "Bourbon"],
                "established_year": 2001,
                "owner": "Gia Lai Green Coffee Co., Ltd",
                "contact": "+84 269 678 901",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - Organic Block", "area": 20.0},
                    {"id": "field_b", "name": "Field B - Traditional Plot", "area": 18.7},
                    {"id": "field_c", "name": "Field C - Research Area", "area": 10.0},
                    {"id": "field_d", "name": "Field D - Sustainable Demo", "area": 7.0}
                ]
            },
            {
                "name": "Cu Chi Specialty Coffee Garden",
                "location": "Cu Chi, Ho Chi Minh City, Vietnam",
                "coordinates": {
                    "latitude": 11.0500,
                    "longitude": 106.4833
                },
                "area_hectares": 22.3,
                "elevation": 25,
                "coffee_varieties": ["Liberica", "Robusta"],
                "established_year": 2015,
                "owner": "Cu Chi Tourism & Agriculture",
                "contact": "+84 28 789 012",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - Lowland Block", "area": 12.0},
                    {"id": "field_b", "name": "Field B - Tourist Area", "area": 6.3},
                    {"id": "field_c", "name": "Field C - Processing Center", "area": 4.0}
                ]
            },
            {
                "name": "Đồng Nai Highland Estate",
                "location": "Cát Tiên, Lâm Đồng, Vietnam",
                "coordinates": {
                    "latitude": 11.4667,
                    "longitude": 107.4167
                },
                "area_hectares": 38.9,
                "elevation": 420,
                "coffee_varieties": ["Robusta", "Catimor", "Chari"],
                "established_year": 1992,
                "owner": "Đồng Nai Plantation Ltd",
                "contact": "+84 251 890 123",
                "plus_code": None,
                "fields": [
                    {"id": "field_a", "name": "Field A - River Bend", "area": 15.0},
                    {"id": "field_b", "name": "Field B - Highland Terrace", "area": 13.9},
                    {"id": "field_c", "name": "Field C - Forest Edge", "area": 10.0}
                ]
            }
        ]
        return additional_farms
    
    async def add_farms_to_database(self, farms_data):
        """Add new farms to Firebase"""
        farms_ref = self.firebase.db.collection('farms')
        added_count = 0
        
        for farm_data in farms_data:
            # Check if farm already exists (by name)
            existing = list(farms_ref.where('name', '==', farm_data['name']).stream())
            
            if not existing:
                # Add created_at timestamp
                farm_data['created_at'] = datetime.now().isoformat()
                farm_data['updated_at'] = None
                
                # Add to Firebase
                doc_ref = farms_ref.document()
                doc_ref.set(farm_data)
                added_count += 1
                print(f"✅ Added: {farm_data['name']}")
            else:
                print(f"⏭️  Skipped (exists): {farm_data['name']}")
        
        return added_count
    
    async def update_farmer_assignments(self):
        """Redistribute farmers across all farms"""
        print("📊 Redistributing farmers across farms...")
        
        # Get all farms and farmers
        farms_ref = self.firebase.db.collection('farms')
        farmers_ref = self.firebase.db.collection('farmers')
        
        farms = []
        for doc in farms_ref.stream():
            farm_data = doc.to_dict()
            farm_data['id'] = doc.id
            farms.append(farm_data)
        
        farmers = []
        for doc in farmers_ref.stream():
            farmer_data = doc.to_dict()
            farmer_data['id'] = doc.id
            farmers.append(farmer_data)
        
        print(f"Found {len(farms)} farms and {len(farmers)} farmers")
        
        # Redistribute farmers evenly across farms
        import random
        random.shuffle(farmers)  # Randomize order
        
        farmers_per_farm = len(farmers) // len(farms)
        remainder = len(farmers) % len(farms)
        
        farmer_index = 0
        updated_count = 0
        
        for i, farm in enumerate(farms):
            # Some farms get one extra farmer if there's remainder
            farm_farmer_count = farmers_per_farm + (1 if i < remainder else 0)
            
            # Assign farmers to this farm
            for j in range(farm_farmer_count):
                if farmer_index < len(farmers):
                    farmer = farmers[farmer_index]
                    
                    # Pick a random field from the farm
                    if farm.get('fields') and len(farm['fields']) > 0:
                        field = random.choice(farm['fields'])
                        field_id = field['id']
                        field_name = field['name']
                    else:
                        field_id = 'field_a'
                        field_name = 'Field A'
                    
                    # Update farmer data
                    farmer_doc = farmers_ref.document(farmer['id'])
                    farmer_doc.update({
                        'farm_id': farm['id'],
                        'farm_name': farm['name'],
                        'field_id': field_id,
                        'field_name': field_name,
                        'section_id': field_id,
                        'section_name': field_name,
                        'updated_at': datetime.now().isoformat()
                    })
                    
                    updated_count += 1
                    farmer_index += 1
        
        print(f"✅ Updated {updated_count} farmer assignments")
        
        # Show distribution
        print("\n📊 FARMER DISTRIBUTION:")
        for farm in farms:
            farm_farmers = [f for f in farmers if f.get('farm_id') == farm['id']]
            print(f"   {farm['name']}: {len(farm_farmers)} farmers")

async def main():
    print("🚀 Adding more coffee farms to database...")
    print("📊 Current Database: kmou-aicofee (Primary)")
    
    expander = FarmExpander()
    
    # Get additional farm data
    new_farms = expander.get_additional_farms()
    print(f"\n📋 Will add {len(new_farms)} new farms:")
    
    for farm in new_farms:
        print(f"   🏢 {farm['name']} - {farm['location']} ({farm['area_hectares']}ha)")
    
    # Add farms to database
    print("\n🔧 Adding farms to database...")
    added_count = await expander.add_farms_to_database(new_farms)
    
    # Update farmer assignments
    await expander.update_farmer_assignments()
    
    # Final summary
    print(f"\n🎉 COMPLETION SUMMARY:")
    print(f"✅ Added {added_count} new coffee farms")
    print(f"✅ Updated farmer assignments across all farms")
    print(f"✅ Database now has diverse farm locations across Vietnam")

if __name__ == "__main__":
    asyncio.run(main())